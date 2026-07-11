#!/usr/bin/env python3
"""Build src/z2ui5_cl_abap2ui5_local.clas.locals_imp.abap from an abap2UI5 checkout.

Pipeline:
  1. Stage all upstream .clas.abap/.intf.abap files (incl. class locals, excl. testclasses)
     together with a stub report and merge them into one file via abapmerge.
  2. Strip the stub report statements from the merged output.
  3. Re-add the abap2UI5-local specific additions (zif_app / zcx_error).
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
            '  z2ui5_cl_http_handler=>run( ).\n'
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
        text = '\n'.join(blk).lower()
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
        assert ready, f'dependency cycle among: {sorted(remaining)}'
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
