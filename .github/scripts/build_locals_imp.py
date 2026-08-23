#!/usr/bin/env python3
"""Build src/z2ui5_cl_abap2ui5_local.clas.locals_imp.abap from an abap2UI5 checkout.

Pipeline:
  1. Stage all upstream .clas.abap/.intf.abap files (incl. class locals, excl. testclasses)
     together with a stub report and merge them into one file via abapmerge.
  2. Strip the stub report statements from the merged output.
  3. Re-add the abap2UI5-local specific additions (zif_app / zcx_error and the
     z2ui5_cl_http_handler entry point, see LOCAL_ADDITIONS).
  4. Rename the persistence tables (z2ui5_t_01 -> z2ui5_t_99, z2ui5_t_91 -> z2ui5_t_98)
     so the local variant stays independent of a regular abap2UI5 installation.
  5. Rebuild the DEFERRED block and topologically sort all interface/class
     definition blocks so every hard reference (inheritance, INTERFACES,
     component access, RAISING of exception classes) is defined before use.

Usage: build_locals_imp.py <upstream-src-dir> <output-file>
Requires node/npx; abapmerge is fetched on demand (npx --yes abapmerge@<pin>).
"""

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

STUB_NAME = 'z2ui5_merge_stub'
ABAPMERGE = 'abapmerge@0.16.8'

# Everything the folded include has to provide that upstream's sources do not.
#
# zif_app / zcx_error are the local stand-ins an app class is written against.
#
# z2ui5_cl_http_handler is the entry point: src/z2ui5_cl_abap2ui5_local on each
# generated branch calls z2ui5_cl_http_handler=>run( ), and that name used to
# arrive from upstream's src/99 - which the input refresh now drops, because a
# self-contained fold has no use for the rest of that package. The name is a
# contract between two files THIS repository owns, so the build supplies it
# here rather than keeping a package alive for one empty subclass. Note that
# the abaplint run in refresh_input.sh cannot see this: it resolves input/,
# and the caller lives on the branch. The generate_* lint is the guard.
LOCAL_ADDITIONS = '''CLASS zcx_error DEFINITION
  INHERITING FROM cx_static_check
  FINAL
  CREATE PUBLIC .

  PUBLIC SECTION.
  PROTECTED SECTION.
  PRIVATE SECTION.
ENDCLASS.
CLASS zcx_error IMPLEMENTATION.
ENDCLASS.

INTERFACE zif_app .

  METHODS run RAISING zcx_error.

ENDINTERFACE.

CLASS z2ui5_cl_http_handler DEFINITION INHERITING FROM z2ui5_cl_ui5_http_handler.

  PUBLIC SECTION.
  PROTECTED SECTION.
  PRIVATE SECTION.

ENDCLASS.

CLASS z2ui5_cl_http_handler IMPLEMENTATION.

ENDCLASS.

'''

TABLE_RENAMES = [
    ('z2ui5_t_01', 'z2ui5_t_99'),
    ('z2ui5_t_91', 'z2ui5_t_98'),
]


def run_abapmerge(upstream_src: Path) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        stage = Path(tmp) / 'src'
        stage.mkdir()
        patterns = ('*.clas.abap', '*.intf.abap',
                    '*.clas.locals_imp.abap', '*.clas.locals_def.abap')
        for pattern in patterns:
            for f in upstream_src.rglob(pattern):
                if 'testclasses' in f.name:
                    continue
                shutil.copy(f, stage / f.name)
        stub = stage / f'{STUB_NAME}.prog.abap'
        stub.write_text(
            f'REPORT {STUB_NAME}.\n\n'
            'START-OF-SELECTION.\n'
            '  z2ui5_cl_ui5_http_handler=>run( ).\n'
        )
        out = Path(tmp) / 'merged.abap'
        subprocess.run(
            ['npx', '--yes', ABAPMERGE, '--allow-unused', '-o', str(out), str(stub)],
            check=True,
        )
        return out.read_text()


def strip_stub(src: str) -> str:
    lines = src.split('\n')
    assert lines[0].startswith(f'REPORT {STUB_NAME}'), 'unexpected merge output'
    lines = lines[1:]
    while lines and lines[0].strip() == '':
        lines = lines[1:]
    out = []
    skip = 0
    for line in lines:
        if line.strip() == 'START-OF-SELECTION.':
            skip = 2  # this line + the run() call
        if skip:
            skip -= 1
            continue
        out.append(line)
    return '\n'.join(out)


def rename_tables(src: str) -> str:
    for old, new in TABLE_RENAMES:
        src = re.sub(old, new, src)
        src = re.sub(old.upper(), new.upper(), src)
        assert not re.search(old, src, re.I), f'{old} still referenced'
    return src


def strip_comments(line: str) -> str:
    """Drop the ABAP comment part of a line, respecting string literals.

    The ordering below reads references out of the definition blocks, and a
    reference that only appears in prose is not one: upstream's ABAP Doc says
    things like "see z2ui5_cl_ui5_handler=>main_end" inside z2ui5_if_client,
    which no compiler cares about but a plain regex happily turns into an edge
    - and enough of those close a cycle that has no counterpart in the code.

    Two comment forms: `*` in column 1 comments out the whole line, `"` starts
    a comment that runs to the end of the line. A `"` inside a literal ('...',
    `...` or |...|) is not a comment, hence the scan rather than a split.
    """
    if line.startswith('*'):
        return ''
    out = []
    i, n = 0, len(line)
    while i < n:
        c = line[i]
        if c == '"':
            break
        if c in ("'", '`'):
            i += 1
            while i < n:
                if line[i] == c:
                    if i + 1 < n and line[i + 1] == c:  # doubled = escaped
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
            continue
        if c == '|':
            i += 1
            while i < n:
                if line[i] == '\\':  # escapes \| \{ \} \\ inside a template
                    i += 2
                    continue
                if line[i] == '|':
                    i += 1
                    break
                i += 1
            continue
        out.append(c)
        i += 1
    return ''.join(out)


def restructure(src: str) -> str:
    """Rebuild the DEFERRED block and order all definitions before use."""
    deferred_if, deferred_cls, body = [], [], []
    for line in src.split('\n'):
        if re.match(r'^CLASS \w+ DEFINITION DEFERRED\.\s*$', line):
            if line not in deferred_cls:
                deferred_cls.append(line)
        elif re.match(r'^INTERFACE \w+ DEFERRED\.\s*$', line):
            if line not in deferred_if:
                deferred_if.append(line)
        else:
            body.append(line)

    blocks, kinds = {}, {}
    kept = []
    first_start = None
    i, n = 0, len(body)
    while i < n:
        m_if = re.match(r'^INTERFACE (\w+)\s*\.\s*$', body[i])
        m_cl = re.match(r'^CLASS (\w+) DEFINITION\b', body[i])
        if m_if and m_if.group(1) == 'lif_abapmerge_marker':
            m_if = None
        if m_if or m_cl:
            name = (m_if or m_cl).group(1)
            end_pat = r'^ENDINTERFACE\s*\.\s*$' if m_if else r'^ENDCLASS\s*\.\s*$'
            pre = []
            while kept and kept[-1].startswith('*') and 'abapmerge' not in kept[-1]:
                pre.insert(0, kept.pop())
            j = i
            while not re.match(end_pat, body[j]):
                j += 1
            end = j + 1
            while end < n and body[end].strip() == '':
                end += 1
            blocks[name] = pre + body[i:end]
            kinds[name] = 'if' if m_if else 'cl'
            if first_start is None:
                first_start = len(kept)
            i = end
            continue
        kept.append(body[i])
        i += 1

    # every block gets a DEFERRED declaration so plain references resolve
    for name, kind in kinds.items():
        if kind == 'if':
            decl = f'INTERFACE {name} DEFERRED.'
            if decl not in deferred_if:
                deferred_if.append(decl)
        else:
            decl = f'CLASS {name} DEFINITION DEFERRED.'
            if decl not in deferred_cls:
                deferred_cls.append(decl)

    def is_exception(name):
        return re.match(r'^(z2ui5_cx_|zcx_)', name) is not None

    def is_renamed_local(name):
        return not re.match(r'^(z2ui5_|zif_|zcx_)', name)

    deps = {}
    for name, blk in blocks.items():
        text = '\n'.join(strip_comments(l) for l in blk).lower()
        wants = set()
        for other in blocks:
            if other == name:
                continue
            o = other.lower()
            if (re.search(rf'\binheriting\s+from\s+{o}\b', text)
                    or re.search(rf'\binterfaces\s+{o}\b', text)
                    or re.search(rf'\b{o}\s*=>', text)
                    or re.search(rf'\b{o}~', text)
                    or (is_exception(other) and re.search(rf'\b{o}\b', text))
                    or (is_renamed_local(other) and kinds[other] == 'if'
                        and re.search(rf'\b{o}\b', text))):
                wants.add(other)
        deps[name] = wants

    ordered = []
    remaining = dict(deps)
    while remaining:
        ready = sorted((k for k, v in remaining.items()
                        if not (v & set(remaining))), key=str.lower)
        if not ready:
            # Name the edges, not just the members: the member list alone says
            # nothing about which reference has to go, and this assert is the
            # only thing the workflow log shows.
            edges = '\n'.join(
                f'  {k} -> {o}'
                for k in sorted(remaining)
                for o in sorted(remaining[k] & set(remaining)))
            raise AssertionError(
                f'dependency cycle among {len(remaining)} definitions:\n{edges}')
        for r in ready:
            ordered.append(r)
            del remaining[r]

    out = deferred_if + deferred_cls + ['']
    out += kept[:first_start]
    for name in ordered:
        out.extend(blocks[name])
    out.extend(kept[first_start:])
    return '\n'.join(out)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    upstream_src = Path(sys.argv[1])
    output = Path(sys.argv[2])

    src = run_abapmerge(upstream_src)
    src = strip_stub(src)

    # abapmerge stamps the merge time into its marker interface; drop it so
    # repeated runs produce identical output and the unchanged-tree check in
    # the generate_* workflows can actually skip the push
    src = re.sub(r'^(\* abapmerge \d+\.\d+\.\d+) - \S+$', r'\1', src, flags=re.M)
    src = re.sub(r'(CONSTANTS c_merge_timestamp TYPE string VALUE )`[^`]*`',
                 r'\1``', src)

    lines = src.split('\n')
    last_deferred = max(i for i, l in enumerate(lines)
                        if l.rstrip().endswith('DEFERRED.'))
    lines = (['INTERFACE zif_app DEFERRED.'] + lines[:last_deferred + 1]
             + ['', ''] + LOCAL_ADDITIONS.split('\n') + lines[last_deferred + 1:])
    src = '\n'.join(lines)

    src = rename_tables(src)
    src = restructure(src)

    # abapGit strips trailing blanks when serializing, so any trailing
    # whitespace here would show up as a diff right after pulling the branch
    src = '\n'.join(line.rstrip() for line in src.split('\n'))

    output.write_text(src)
    version = re.search(r"CONSTANTS version TYPE string VALUE `([^`]+)`", src)
    print(f'written {output} ({src.count(chr(10))} lines, '
          f'abap2UI5 version {version.group(1) if version else "unknown"})')


if __name__ == '__main__':
    main()
