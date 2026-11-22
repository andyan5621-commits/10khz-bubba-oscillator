"""Check current documentation links, evidence hashes and data transcriptions.

Run with Python 3 from any directory. No third-party packages required.
Link checking covers every tracked Markdown document, including historical
snapshots. Checks read original design artifacts without changing them.
"""
from pathlib import Path
from urllib.parse import unquote
import csv
from decimal import Decimal
import hashlib
import json
import math
import re
import subprocess

root = Path(__file__).resolve().parents[1]
files = [name for name in subprocess.check_output(
    ['git', 'ls-files', '-z'], cwd=root).decode('utf-8').split('\0')
    if name.endswith('.md')]
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
archive_ok = hashlib.sha256(archive.read_bytes()).hexdigest() == expected_hash
if not archive_ok:
    errors.append('Released archive hash mismatch')
board = root/'pcb/R1/fabrication/review-packages/R1-review-03/source/oscillator.kicad_pcb'
board_ok = hashlib.sha256(board.read_bytes()).hexdigest() == 'a4f358f10eaf822501065362decd702d36b8ac9826cc2c7e55d44460478eb4e2'
if not board_ok:
    errors.append('Reviewed native board hash mismatch')

csv_rows = 0
datasets = {}
for name, count in [('pcb-amplitude-sweep.csv',7),('breadboard-amplitude-sweep.csv',9),('pcb-repeat-captures.csv',3)]:
    with (root/'results/hardware'/name).open(encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    datasets[name] = rows
    csv_rows += len(rows)
    if len(rows) != count:
        errors.append(f'{name}: unexpected row count')
    for row in rows:
        if not all(math.isfinite(float(value)) for value in row.values()):
            errors.append(f'{name}: non-finite numeric value')
        vpp=row.get('calculated_vpp_v', row.get('approx_vpp_v'))
        if abs(float(vpp)-2*float(row['displayed_vpk_v'])) > 1e-9:
            errors.append(f'{name}: Vpp conversion mismatch')

# Check the published numeric tables against the CSV transcriptions rather than
# merely checking row counts or mirrored arithmetic.
report = (root/'docs/report/final-project-report.md').read_text(encoding='utf-8')
tables = [[cell.strip() for cell in line.strip('|').split('|')]
          for line in report.splitlines() if line.startswith('|')]
breadboard = {Decimal(r['approx_vpp_v']):r
              for r in datasets['breadboard-amplitude-sweep.csv']}
for row in datasets['pcb-amplitude-sweep.csv']:
    expected = [row['displayed_vpk_v'], row['calculated_vpp_v'],
                row['reported_frequency_hz'], row['reported_spectral_estimate_db'],
                breadboard[Decimal(row['calculated_vpp_v'])]['cursor_separation_db']]
    if not any(len(t)==5 and all(
            re.fullmatch(r'[\d.]+',cell) and Decimal(cell)==Decimal(value)
            for cell,value in zip(t,expected)) for t in tables):
        errors.append('Report amplitude row differs from CSV: '+str(expected))
for row in datasets['pcb-repeat-captures.csv']:
    expected = [row['capture'],row['frequency_hz'],row['displayed_vpk_v'],
                row['cursor_difference_db'],row['sinad_db']]
    if not any(len(t)==5 and all(
            re.fullmatch(r'[\d.]+',cell) and Decimal(cell)==Decimal(value)
            for cell,value in zip(t,expected)) for t in tables):
        errors.append('Report repeated capture differs from CSV: '+str(expected))

result = {'markdown_files_checked':len(files),'local_links_checked':links,
          'evidence_files_checked':len(manifest),
          'released_archive_hash_verified':archive_ok,'reviewed_board_hash_verified':board_ok,
          'hardware_csv_rows_checked':csv_rows,'report_tables_compared_to_csv':True,
          'errors':errors}
print(json.dumps(result,indent=2))
raise SystemExit(bool(errors))
