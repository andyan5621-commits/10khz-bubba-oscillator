from pathlib import Path
import csv,json
ns={};exec(Path('oscillator-pcb/verification/check_board_parity.py').read_text().split('netpath,boardpath=')[0],ns)
parse,children,one,val=ns['parse'],ns['children'],ns['one'],ns['val']
b=parse(Path('oscillator-pcb/verification/final-independent-export.net').read_text());cs={val(c,'ref'):c for c in children(one(b,'components'),'comp')}
rows=list(csv.DictReader(Path('oscillator-pcb/bom/per-component.csv').open(encoding='utf-8-sig')));refs=[r['Reference'] for r in rows];fail=[]
if len(refs)!=len(set(refs)):fail.append('Duplicate BOM references')
if set(refs)!=set(cs):fail.append('BOM reference set differs from schematic')
for r in rows:
 c=cs.get(r['Reference'])
 if not c:continue
 for label,k in [('Value','value'),('Footprint','footprint')]:
  if r[label]!=val(c,k):fail.append(f'{r["Reference"]}: {label} mismatch')
 properties={val(p,'name'):val(p,'value') for p in children(c,'property')}
 if properties.get('MPN') and r['MPN']!=properties['MPN']:fail.append(f'{r["Reference"]}: MPN differs from populated schematic MPN')
 if not r['MPN']:fail.append(f'{r["Reference"]}: BOM MPN missing')
 if r['Reference'].startswith('TP') and (r['MPN']!='BARE_PCB_PROBE_PAD' or r['Status']!='NO_PURCHASE'):fail.append(f'{r["Reference"]}: expected bare PCB probe pad')
 if r['Quantity']!='1':fail.append(f'{r["Reference"]}: per-part quantity not1')
print(json.dumps({'scope':'Complete reference/value/footprint parity; populated schematic MPNs agree. Resistor MPN sourcing stays in BOM, as schematic resistor MPN fields are absent.','verdict':'FAIL' if fail else 'PASS','components':len(rows),'resistors':sum(r.startswith('R') and not r.startswith('RV') for r in refs),'failures':fail},indent=2))
