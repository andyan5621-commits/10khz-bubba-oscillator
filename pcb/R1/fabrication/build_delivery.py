"""Assemble the reviewed R1 delivery without altering the audited candidate."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'deliverables' / 'R1-engineering-review'
CAND = Path('fabrication/review-packages/R1-review-03')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def copy(relative):
    src = ROOT / relative
    dst = DEST / relative
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

if DEST.exists():
    raise SystemExit('Refusing to overwrite an existing delivery snapshot')
DEST.mkdir(parents=True)
for src in (ROOT / CAND).rglob('*'):
    if src.is_file():
        copy(src.relative_to(ROOT))
for directory in ('assembly', 'bom'):
    for src in (ROOT / directory).rglob('*'):
        if src.is_file() and src.suffix in ('.md', '.csv', '.pdf', '.json'):
            copy(src.relative_to(ROOT))
for name in ('final-engineering-summary', 'layout', 'export-inspection',
             'fabrication', 'task-board', 'decision-log', 'risk-register', 'revision-status'):
    copy(Path('reports') / (name + '.md'))
for name in ('ordering-guidance.md', 'rule-target.md'):
    copy(Path('fabrication') / name)
for src in (ROOT / 'verification').glob('*'):
    if src.is_file() and (src.name.startswith('final-') or src.name in (
        'independent-review.md', 'footprint-audit.md', 'alps-slot-manufacturing-review.md',
        'drill-coordinate-parity-results.json', 'package-integrity-results.json',
        'package-erc-independent.json', 'package-drc-independent.json',
        'silk-variant-independent-results.json', 'pad-geometry-stability-results.json',
        'mounting-clearance-results.json', 'vout-adjacency-final.json')):
        copy(src.relative_to(ROOT))
for name in ('board-top.png', 'board-3d.png', 'board-front.svg', 'board-back.svg',
             'mechanical-outline.svg'):
    copy(Path('pcb') / name)
for src in (ROOT / 'fabrication/inspection/results/R1-review-03').glob('*'):
    if src.is_file():
        copy(src.relative_to(ROOT))
for name in ('fresh-validation-2026-10-22.md', 'layout-risk-assessment.md'):
    copy(Path('simulation') / name)
for src in (ROOT / 'reference').rglob('*'):
    if src.is_file():
        copy(src.relative_to(ROOT))
copy(Path('README.md'))
with (DEST / 'README.md').open('a', encoding='utf-8') as f:
    f.write('''
## Delivery contents and integrity

This consolidated delivery contains the immutable R1-review-03 candidate and the final independent review and operating documentation. Open the native KiCad project through the link above. Only the Gerber/drill ZIP is the proposed fabrication input; do not upload this complete documentation archive to order boards. Follow [ordering guidance](fabrication/ordering-guidance.md).

The candidate's original SHA256.json applies relative to its own directory. The outer SHA256.json covers every delivered file except itself. Reports retain workspace-relative evidence references; detailed simulation waveforms and intermediate engineering history remain in the version-controlled project workspace rather than this delivery.

The parasitic-risk report records an earlier request to rework VOUT. The final design removes its redundant loop; the remaining route was reviewed and accepted in decision D017 and the final independent report. Some capacitor, connector and potentiometer body models are absent from the 3D preview, which is not an enclosure-fit model.

Gates A–D passed. User fabrication release, live quote approval, incoming fit checks, assembly and measured hardware validation remain outstanding. No upload, order or physical PCB test has occurred.
''')

gates = json.loads((ROOT / 'verification/final-gate-results.json').read_text())
checks = {
    CAND / 'source/oscillator.kicad_pcb': gates['native_board_sha256'],
    CAND / 'source/oscillator.kicad_sch': gates['native_schematic_sha256'],
    CAND / 'R1-review-03-gerbers-UNRELEASED.zip': gates['gerber_zip_sha256'],
    Path('verification/independent-review.md'): gates['independent_review_sha256'],
}
for rel, expected in checks.items():
    assert sha(DEST / rel) == expected, rel
original_manifest = json.loads((DEST / CAND / 'SHA256.json').read_text())
for name, expected in original_manifest.items():
    assert sha(DEST / CAND / name.replace('\\', '/')) == expected, name
manifest = {p.relative_to(DEST).as_posix(): sha(p)
            for p in sorted(DEST.rglob('*')) if p.is_file()}
(DEST / 'SHA256.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
archive = DEST.parent / 'Oscillator-PCB-R1-Engineering-Review.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for p in sorted(DEST.rglob('*')):
        if p.is_file():
            z.write(p, p.relative_to(DEST.parent).as_posix())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for name, expected in manifest.items():
        assert hashlib.sha256(z.read(DEST.name + '/' + name)).hexdigest() == expected
result = {'status': 'PASS', 'files_hashed': len(manifest),
          'original_candidate_hashes_verified': len(original_manifest),
          'archive': archive.name, 'archive_sha256': sha(archive),
          'archive_bytes': archive.stat().st_size,
          'audited_board_schematic_gerber_and_report_match': True,
          'user_release_authorized': False}
(DEST.parent / 'delivery-integrity.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
