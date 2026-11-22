"""Check current documentation links, evidence hashes and data transcriptions.

Run with Python 3 from any directory. No third-party packages required.
Historical snapshot documents are intentionally outside the link-check scope.
"""
from pathlib import Path
from urllib.parse import unquote
import csv
import hashlib
import json
import re
import statistics

root = Path(__file__).resolve().parents[1]
files = ['README.md', 'CHANGELOG.md', 'docs/README.md', 'docs/measurements.md',
         'docs/report/final-project-report.md', 'pcb/README.md', 'pcb/R1/README.md',
         'results/hardware/README.md', 'evidence/hardware/2026-11-20/README.md',
         'pcb/R1/fabrication/releases/R1/RELEASE.md',
         'pcb/R1/reports/project-closeout.md',
         'pcb/R1/assembly/R1-detailed-soldering-guide.md',
         'pcb/R1/assembly/assembly-and-test.md',
         'pcb/R1/assembly/drawings/clear-map/README.md']
errors = []
links = 0
for name in files:
    p = root / name
    for target in re.findall(r'\]\(([^)]+)\)', p.read_text(encoding='utf-8')):
        if re.match(r'^(https?://|#|mailto:)', target):
            continue
        links += 1
        local = unquote(target.split('#')[0])
        if not (p.parent / local).exists():
            errors.append(f'{name}: missing {target}')

e = root / 'evidence/hardware/2026-11-20'
manifest = json.loads((e/'manifest-sha256.json').read_text(encoding='utf-8'))
for name, expected in manifest.items():
    if hashlib.sha256((e/name).read_bytes()).hexdigest() != expected:
        errors.append(f'Changed evidence: {name}')

expected_hash = 'b7150ff62d955080c8e8bda7e1d0696d12e3df7a49b8af16baf8273b0053b478'
archive = root/'pcb/R1/fabrication/releases/R1/Oscillator-PCB-R1-Gerbers.zip'
if hashlib.sha256(archive.read_bytes()).hexdigest() != expected_hash:
    errors.append('Released archive hash mismatch')
board = root/'pcb/R1/fabrication/review-packages/R1-review-03/source/oscillator.kicad_pcb'
if hashlib.sha256(board.read_bytes()).hexdigest() != 'a4f358f10eaf822501065362decd702d36b8ac9826cc2c7e55d44460478eb4e2':
    errors.append('Reviewed native board hash mismatch')

for name, count in [('pcb-amplitude-sweep.csv',7),('breadboard-amplitude-sweep.csv',9),('pcb-repeat-captures.csv',3)]:
    with (root/'results/hardware'/name).open(encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    if len(rows) != count:
        errors.append(f'{name}: unexpected row count')
    for row in rows:
        vpp=row.get('calculated_vpp_v', row.get('approx_vpp_v'))
        if abs(float(vpp)-2*float(row['displayed_vpk_v'])) > 1e-9:
            errors.append(f'{name}: Vpp conversion mismatch')

result = {'local_links_checked':links,'evidence_files_verified':len(manifest),
          'released_archive_hash_verified':True,'reviewed_board_hash_verified':True,
          'hardware_csv_rows_checked':19,'errors':errors}
print(json.dumps(result,indent=2))
raise SystemExit(bool(errors))
