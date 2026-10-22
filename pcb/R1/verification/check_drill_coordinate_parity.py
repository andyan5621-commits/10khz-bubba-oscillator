from pathlib import Path
import json,re,math,collections
ns={};exec(Path('oscillator-pcb/verification/check_board_parity.py').read_text().split('netpath,boardpath=')[0],ns);parse,c,o=ns['parse'],ns['children'],ns['one']
root=Path('oscillator-pcb/fabrication/review-packages/R1-review-03');b=parse((root/'source/oscillator.kicad_pcb').read_text());expected={'PTH':[],'NPTH':[]}
def key(d,a,z=None):return tuple(round(v,3) for v in [d,*a,*(() if z is None else z)])
for v in c(b,'via'):expected['PTH'].append(key(float(o(v,'drill')[1]),list(map(float,o(v,'at')[1:3]))))
for f in c(b,'footprint'):
 at=list(map(float,o(f,'at')[1:]));ang=math.radians(at[2] if len(at)>2 else 0)
 for p in c(f,'pad'):
  if p[2] not in ['thru_hole','np_thru_hole']:continue
  x,y=map(float,o(p,'at')[1:3]);pos=[at[0]+x*math.cos(ang)+y*math.sin(ang),at[1]-x*math.sin(ang)+y*math.cos(ang)];dr=o(p,'drill')[1:];kind='PTH' if p[2]=='thru_hole' else 'NPTH'
  if dr[0]=='oval':
   dx,dy=map(float,dr[1:]);a=float(o(p,'at')[3]) if len(o(p,'at'))>3 else 0;a=math.radians(a);travel=(dx-dy)/2;offset=[travel*math.cos(a),-travel*math.sin(a)];ends=sorted([[pos[0]-offset[0],pos[1]-offset[1]],[pos[0]+offset[0],pos[1]+offset[1]]]);expected[kind].append(key(min(dx,dy),*ends))
  else:expected[kind].append(key(float(dr[0]),pos))
results={}
for kind in expected:
 lines=(root/f'gerbers/oscillator-{kind}.drl').read_text().splitlines();tools={};tool=None;start=None;actual=[]
 for line in lines:
  m=re.fullmatch(r'T(\d+)C([\d.]+)',line)
  if m:tools[m[1]]=float(m[2]);continue
  m=re.fullmatch(r'T(\d+)',line)
  if m:tool=m[1];continue
  m=re.fullmatch(r'(G00|G01)?X([\d.-]+)Y([\d.-]+)',line)
  if not m:continue
  xy=[float(m[2]),-float(m[3])]
  if m[1]=='G00':start=xy
  elif m[1]=='G01':actual.append(key(tools[tool],*sorted([start,xy])))
  else:actual.append(key(tools[tool],xy))
 missing=list((collections.Counter(expected[kind])-collections.Counter(actual)).elements());extra=list((collections.Counter(actual)-collections.Counter(expected[kind])).elements())
 results[kind]={'native_features':len(expected[kind]),'exported_features':len(actual),'missing':missing,'extra':extra}
results['verdict']='PASS' if all(not x['missing'] and not x['extra'] for k,x in results.items()) else 'FAIL'
print(json.dumps(results,indent=2));assert results['verdict']=='PASS'
