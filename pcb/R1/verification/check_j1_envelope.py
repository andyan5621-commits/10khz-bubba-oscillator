"""Independent conservative connector envelope calculation from the native board."""
from pathlib import Path
import json, math, re, hashlib
def parse(text):
    root=[]; active=root; stack=[]
    for t in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', text):
        if t=='(':
            child=[]; active.append(child); stack.append(active); active=child
        elif t==')': active=stack.pop()
        else: active.append(json.loads(t) if t.startswith('"') else t)
    return root[0]
def children(n,k): return [c for c in n if isinstance(c,list) and c and c[0]==k]
def one(n,k): return next(iter(children(n,k)),[k])
path=Path(__file__).resolve().parents[1]/'pcb/oscillator.kicad_pcb'
board=parse(path.read_text(encoding='utf-8'))
footprints=children(board,'footprint')
j1=next(f for f in footprints if any(p[1:3]==['Reference','J1'] for p in children(f,'property')))
at=list(map(float,one(j1,'at')[1:])); angle=math.radians(at[2] if len(at)>2 else 0)
def transform(p):
    x,y=map(float,p)
    return [at[0]+x*math.cos(angle)+y*math.sin(angle),at[1]-x*math.sin(angle)+y*math.cos(angle)]
rect=next(r for r in children(j1,'fp_rect') if one(r,'layer')[1]=='F.CrtYd')
start=one(rect,'start')[1:]; end=one(rect,'end')[1:]
corners=[transform([x,y]) for x in [start[0],end[0]] for y in [start[1],end[1]]]
edges=[e for e in children(board,'gr_line') if one(e,'layer')[1]=='Edge.Cuts']
edgepoints=[list(map(float,one(e,k)[1:])) for e in edges for k in ['start','end']]
bounds=lambda ps:[min(p[0] for p in ps),min(p[1] for p in ps),max(p[0] for p in ps),max(p[1] for p in ps)]
cb=bounds(corners); bb=bounds(edgepoints)
margins=[cb[0]-bb[0],cb[1]-bb[1],bb[2]-cb[2],bb[3]-cb[3]]
local=list(map(float,start+end))
assert local[0]<=-3.25 and local[2]>=13.25 and local[1]<=-10 and local[3]>=10
assert min(margins)>0
result={'verdict':'PASS','scope':'J1 conservative courtyard bounds; neighbor collision checked by independent KiCad DRC',
 'board_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'courtyard_local_xyxy_mm':local,
 'courtyard_board_xyxy_mm':cb,'rectangular_board_bounds_xyxy_mm':bb,'board_edge_margins_left_top_right_bottom_mm':margins,
 'body_datum_status':'Centered Fab outline illustrative only; independent pin-row depth datum remains unverified',
 'envelope_basis':'9.5 mm full nominal body depth allowed on either side of row, plus 0.5 mm; nominal width extended 0.75 mm at each end'}
print(json.dumps(result,indent=2))
