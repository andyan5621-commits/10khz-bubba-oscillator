from pathlib import Path
import hashlib,json,zipfile
root=Path('oscillator-pcb/fabrication/review-packages/R1-review-03');manifest=json.loads((root/'SHA256.json').read_text());fail=[]
for rel,expected in manifest.items():
 p=root/rel
 if not p.exists():fail.append('Missing '+rel)
 elif hashlib.sha256(p.read_bytes()).hexdigest()!=expected:fail.append('Hash mismatch '+rel)
zpath=root/'R1-review-03-gerbers-UNRELEASED.zip'
with zipfile.ZipFile(zpath) as z:
 actual={n for n in z.namelist() if not n.endswith('/')};wanted={p.name for p in (root/'gerbers').iterdir() if p.is_file()}
 if actual!=wanted:fail.append('ZIP file set differs from inspected gerbers folder')
 for name in actual:
  if z.read(name)!=(root/'gerbers'/name).read_bytes():fail.append('ZIP bytes differ '+name)
provenance=json.loads((root/'source-provenance.json').read_text())
for rel,h in provenance.items():
 src=Path('oscillator-pcb')/rel;pkg=root/'source'/Path(rel).name
 if hashlib.sha256(src.read_bytes()).hexdigest()!=h:fail.append('Workspace provenance mismatch '+rel)
 if hashlib.sha256(pkg.read_bytes()).hexdigest()!=h:fail.append('Package provenance mismatch '+rel)
print(json.dumps({'verdict':'FAIL' if fail else 'PASS','package':str(root),'manifest_entries_verified':len(manifest),'gerber_zip_entries':len(actual),'zip_sha256':hashlib.sha256(zpath.read_bytes()).hexdigest(),'failures':fail},indent=2))

