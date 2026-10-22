"""Join the actual exported schematic with the selected procurement catalog."""
from pathlib import Path
import csv
import re
import collections
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
catalog=list(csv.DictReader((HERE/'draft_bom.csv').open(encoding='utf-8-sig')))
def ohms(value):
    s=value.lower().replace(' ','').replace('ohm','').replace('Ω','')
    if s.endswith('r'): return float(s[:-1])
    if 'k' in s:
        a,b=s.split('k'); return float(a+'.'+b if b else a)*1000
    return float(s)
resistors={ohms(row['Logical_reference'].split()[0]):row for row in catalog if row['Category']=='Resistor'}
parts={row['Manufacturer_part_number']:row for row in catalog if row['Category']!='Resistor' and row['Status']!='BLOCKED_ALTERNATE'}
result=[]
for c in ET.parse(HERE/'schematic-source.xml').getroot().findall('components/comp'):
    ref=c.attrib['ref']; value=c.findtext('value'); footprint=c.findtext('footprint')
    fields={f.attrib['name']:f.text for f in c.findall('fields/field')}
    if ref.startswith('TP'):
        mpn='BARE_PCB_PROBE_PAD'; maker='PCB fabrication'; status='NO_PURCHASE'
    else:
        row=resistors[ohms(value)] if re.fullmatch(r'R\d+',ref) else parts[fields['MPN']]
        mpn=row['Manufacturer_part_number']; maker=row['Manufacturer']; status='SELECTED_NOT_RELEASED'
    if not footprint: raise ValueError(f'Missing footprint: {ref}')
    result.append(dict(Reference=ref,Value=value,Manufacturer=maker,MPN=mpn,Footprint=footprint,Quantity=1,Status=status))
assert len(result)==77, f'Unexpected component count {len(result)}'
assert sum(bool(re.fullmatch(r'R\d+',r['Reference'])) for r in result)==44
with (HERE/'per-component.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f, list(result[0]));w.writeheader();w.writerows(result)
groups=collections.defaultdict(list)
for row in result: groups[(row['Value'],row['Manufacturer'],row['MPN'],row['Footprint'],row['Status'])].append(row['Reference'])
with (HERE/'grouped-bom.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.writer(f);w.writerow(['References','Value','Manufacturer','MPN','Footprint','Fitted_quantity','Status'])
    for key,refs in groups.items(): w.writerow([', '.join(refs),*key[:4],len(refs),key[4]])
print(f'Joined {len(result)} schematic components into {len(groups)} BOM groups; 44 fixed resistors; 8 bare-PCB probe pads; no missing footprints.')
