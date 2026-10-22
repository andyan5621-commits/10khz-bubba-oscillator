from pathlib import Path
import json,math
ns={};exec(Path('oscillator-pcb/verification/check_board_parity.py').read_text().split('netpath,boardpath=')[0],ns)
p,c,o=ns['parse'],ns['children'],ns['one'];b=p(Path('oscillator-pcb/pcb/routing-candidate.kicad_pcb').read_text());pads=[];mounts=[]
for f in c(b,'footprint'):
 ref=next(q[2] for q in c(f,'property') if q[1]=='Reference');at=list(map(float,o(f,'at')[1:]));a=math.radians(at[2] if len(at)>2 else 0)
 if ref in ['H1','H2','H3','H4']:mounts.append((ref,at[:2]));continue
 for pad in c(f,'pad'):
  x,y=map(float,o(pad,'at')[1:3]);xy=(at[0]+x*math.cos(a)+y*math.sin(a),at[1]-x*math.sin(a)+y*math.cos(a));size=list(map(float,o(pad,'size')[1:3]));radius=math.hypot(*size)/2
  pads.append((ref,pad[1],xy,radius))
results=[]
for ref,xy in mounts:
 near=min(((math.dist(xy,pos)-rad,r,pin) for r,pin,pos,rad in pads))
 results.append({'mount':ref,'minimum_conservative_distance_to_any_pad_copper_mm':near[0],'nearest_pad':near[1]+'.'+near[2],'required_hardware_radius_mm':3.05})
assert all(r['minimum_conservative_distance_to_any_pad_copper_mm']>3.05 for r in results)
print(json.dumps({'verdict':'PASS','scope':'Pads stay outside 3.05 mm hardware radius using conservative circumscribed pad circles; DRC verifies track/via/pour keepouts','holes':results},indent=2))
