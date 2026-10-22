from pathlib import Path
import math,json
ns={};exec(Path('oscillator-pcb/verification/check_routing_lengths.py').read_text().split('bp=[]')[0],ns)
c,o=ns['children'],ns['one'];segs=[]
for s in c(ns['b'],'segment'):
 a=tuple(map(float,o(s,'start')[1:]));b=tuple(map(float,o(s,'end')[1:]));v=(b[0]-a[0],b[1]-a[1]);l=math.hypot(*v)
 if l<2:continue
 segs.append((ns['names'][o(s,'net')[1]],o(s,'layer')[1],a,b,(v[0]/l,v[1]/l),l))
near=[]
for n,ly,a,b,u,l in segs:
 if n!='/VOUT':continue
 for m,ml,d,e,v,ll in segs:
  if m==n or ml!=ly or abs(u[0]*v[1]-u[1]*v[0])>.01:continue
  distance=abs((d[0]-a[0])*u[1]-(d[1]-a[1])*u[0]);t=[(x[0]-a[0])*u[0]+(x[1]-a[1])*u[1] for x in [d,e]];overlap=min(l,max(t))-max(0,min(t))
  if distance<2 and overlap>2:near.append({'other_net':m,'centerline_separation_mm':distance,'parallel_overlap_mm':overlap,'VOUT_segment':[a,b],'other_segment':[d,e]})
near.sort(key=lambda x:-x['parallel_overlap_mm'])
print(json.dumps(near,indent=2))
