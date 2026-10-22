from pathlib import Path
import json, math, re, hashlib
source=Path('oscillator-pcb/verification/check_board_parity.py').read_text()
ns={}
exec(source.split('netpath,boardpath=')[0],ns)
parse,children,one=ns['parse'],ns['children'],ns['one']
p=Path('oscillator-pcb/pcb/oscillator.kicad_pcb')
b=parse(p.read_text(encoding='utf-8-sig'))
f=next(f for f in children(b,'footprint') if any(x[1:3]==['Reference','RV1'] for x in children(f,'property')))
results=[]
for pad in children(f,'pad'):
    size=list(map(float,one(pad,'size')[1:]));drill=one(pad,'drill')[1:]
    if drill[0]=='oval':
        dx,dy=map(float,drill[1:]);px,py=size
        ratio=float(one(pad,'roundrect_rratio')[1]);corner=min(size)*ratio
        assert (px,py,dx,dy,corner)==(4,3,2.1,1.8,.75)
        # Full slot boundary sampled as a check on the analytic 0.60 mm minimum.
        gaps=[]
        for k in range(36001):
            a=2*math.pi*k/36000
            x=(dx-dy)/2*(1 if math.cos(a)>=0 else -1)+dy/2*math.cos(a)
            y=dy/2*math.sin(a)
            qx=abs(x)-(px/2-corner);qy=abs(y)-(py/2-corner)
            sdf=math.hypot(max(qx,0),max(qy,0))+min(max(qx,qy),0)-corner
            gaps.append(-sdf)
        minimum=min(gaps)
        assert minimum>=.3
        results.append({'pad':pad[1],'copper_mm':size,'drill_oval_mm':[dx,dy],'copper_corner_radius_mm':corner,'minimum_ring_mm':minimum,'minimum_required_ring_mm':.3,'PTH_slot_tool_diameter_mm':dy,'accepted_tool_range_mm':[.7,2.6]})
    else:
        ring=(min(size)-float(drill[0]))/2
        assert ring>=.3
        results.append({'pad':pad[1],'minimum_ring_mm':ring,'minimum_required_ring_mm':.3})
print(json.dumps({'verdict':'PASS','scope':'RV1 manufactured copper/hole geometry against AISLER ring and slot-tool rules; not terminal insertion proof','board_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'pads':results},indent=2))
