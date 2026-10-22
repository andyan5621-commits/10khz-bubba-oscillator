"""Build an immutable, portable review copy after the native board is routed.

This does not approve or purchase fabrication. It refuses an existing target.
Run with the KiCad bundled Python so the source board can be inspected.
"""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess
import pcbnew

ROOT = Path(__file__).resolve().parents[1]
CLI = Path(r'C:\Program Files\KiCad\9.0\bin\kicad-cli.exe')
parser = argparse.ArgumentParser()
parser.add_argument('revision', help='Unique candidate label, e.g. R1-review-01')
args = parser.parse_args()
if not args.revision.replace('-', '').replace('_', '').isalnum():
    raise SystemExit('Revision must be a simple label')
destination = ROOT / 'fabrication' / 'review-packages' / args.revision
if destination.exists():
    raise SystemExit('Refusing to overwrite an existing review snapshot')
board_source = ROOT / 'pcb' / 'oscillator.kicad_pcb'
board = pcbnew.LoadBoard(str(board_source))
if not any(True for _ in board.GetTracks()):
    raise SystemExit('Board has no routing; no manufacturing review package created')
source_paths = [ROOT/'schematic'/'oscillator.kicad_sch', board_source,
                ROOT/'pcb'/'oscillator.kicad_pro', ROOT/'pcb'/'oscillator.kicad_dru']
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
before = {str(p.relative_to(ROOT)): digest(p) for p in source_paths}
source = destination / 'source'
source.mkdir(parents=True)
for path in source_paths:
    shutil.copy2(path, source/path.name)
shutil.copy2(ROOT/'schematic'/'Oscillator.kicad_sym', source/'Oscillator.kicad_sym')
shutil.copytree(ROOT/'pcb'/'Oscillator.pretty', source/'Oscillator.pretty')
table = (ROOT/'schematic'/'sym-lib-table').read_text(encoding='utf-8')
table = table.replace('C:/Program Files/KiCad/9.0/share/kicad/symbols/', '${KICAD9_SYMBOL_DIR}/')
(source/'sym-lib-table').write_text(table, encoding='utf-8')
(source/'fp-lib-table').write_text(
    '(fp_lib_table (version 7) (lib (name "Oscillator")(type "KiCad")'
    '(uri "${KIPRJMOD}/Oscillator.pretty")(options "")(descr "Reviewed project footprints")))\n',
    encoding='utf-8')
reports = destination/'checks'
reports.mkdir()
def run(label, arguments):
    result = subprocess.run([str(CLI), *map(str, arguments)], capture_output=True,
                            text=True, encoding='utf-8', errors='replace')
    (reports/f'{label}-console.txt').write_text(result.stdout+'\n'+result.stderr, encoding='utf-8')
    if result.returncode:
        raise SystemExit(f'{label} failed ({result.returncode}); candidate remains UNRELEASED')
run('erc', ['sch','erc','--exit-code-violations','--output',reports/'erc.rpt',source/'oscillator.kicad_sch'])
run('drc', ['pcb','drc','--schematic-parity','--exit-code-violations','--output',reports/'drc.rpt',source/'oscillator.kicad_pcb'])
run('netlist', ['sch','export','netlist','--output',reports/'oscillator.net',source/'oscillator.kicad_sch'])
gerbers = destination/'gerbers'
gerbers.mkdir()
run('gerber', ['pcb','export','gerbers','--output',str(gerbers)+'/', '--layers',
    'F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,Edge.Cuts','--subtract-soldermask',source/'oscillator.kicad_pcb'])
run('drill', ['pcb','export','drill','--output',str(gerbers)+'/',
    '--format','excellon','--drill-origin','absolute','--excellon-units','mm',
    '--excellon-oval-format','route','--excellon-separate-th',source/'oscillator.kicad_pcb'])
for folder in ['bom','assembly']:
    shutil.copytree(ROOT/folder, destination/folder, ignore=shutil.ignore_patterns('*.py','__pycache__'))
after = {str(p.relative_to(ROOT)): digest(p) for p in source_paths}
if after != before:
    raise SystemExit('Source changed during packaging; candidate is INVALID and must not be released')
(destination/'STATUS.txt').write_text(
    'UNRELEASED REVIEW CANDIDATE\nRequires independent export inspection and explicit user release/purchase approval.\n'
    'Open source/oscillator.kicad_pro in KiCad 9. Libraries use normal KiCad 9 environment variables.\n',encoding='utf-8')
(destination/'source-provenance.json').write_text(json.dumps(before,indent=2),encoding='utf-8')
manifest = {str(p.relative_to(destination)):digest(p) for p in destination.rglob('*') if p.is_file()}
(destination/'SHA256.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
shutil.make_archive(str(destination/f'{args.revision}-gerbers-UNRELEASED'),'zip',gerbers)
print(destination)
