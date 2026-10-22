import json
from pathlib import Path
old=json.loads(Path('oscillator-pcb/verification/board-parity-results.json').read_text(encoding='utf-8-sig'));new=json.loads(Path('oscillator-pcb/verification/routed-parity-results.json').read_text(encoding='utf-8-sig'))
a={(p['ref'],p['pin']):p for p in old['pad_geometry']};b={(p['ref'],p['pin']):p for p in new['pad_geometry']};diff=[{'pad':k,'before':a[k],'after':b.get(k)} for k in a if a[k]!=b.get(k)]
print(json.dumps({'verdict':'PASS' if not diff else 'REVIEW','scope':'All electrical pad local dimensions and drill geometry versus Gate B accepted snapshot','differences':diff},indent=2))
