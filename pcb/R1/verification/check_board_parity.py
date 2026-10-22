"""Independent native-board pad to exported-schematic net comparison.

Usage: python verification/check_board_parity.py schematic/oscillator.net pcb/oscillator.kicad_pcb
Missing components fail; unnetted pads explicitly named MP* are mechanical only.
This is not a track-connectivity, DRC, or fabrication check.
"""
from pathlib import Path
import collections,hashlib,json,re,sys
def parse(text):
    tokens=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',text)
    root=[];active=root;stack=[]
    for t in tokens:
        if t=='(':
            child=[];active.append(child);stack.append(active);active=child
        elif t==')':active=stack.pop()
        else:active.append(json.loads(t) if t.startswith('"') else t)
    if stack:raise ValueError('Unbalanced file')
    return root[0]
def children(n,k):return [c for c in n if isinstance(c,list) and c and c[0]==k]
def one(n,k):return next(iter(children(n,k)),[k])
def val(n,k,d=''):return (one(n,k)+[d])[1]
netpath,boardpath=map(Path,sys.argv[1:3]);netdoc=parse(netpath.read_text(encoding='utf-8-sig'));board=parse(boardpath.read_text(encoding='utf-8-sig'))
comps={val(c,'ref'):c for c in children(one(netdoc,'components'),'comp')};nets={};fail=[]
for n in children(one(netdoc,'nets'),'net'):
    for p in children(n,'node'):nets[(val(p,'ref'),val(p,'pin'))]=val(n,'name').removeprefix('/')
fps={};padnets={};mechanical=[];pad_geometry=[]
authorized_holes={'H1':(53.5,50.5),'H2':(141.5,50.5),'H3':(53.5,122.5),'H4':(141.5,122.5)}
for f in children(board,'footprint'):
    props={p[1]:p[2] for p in children(f,'property')}
    ref=props.get('Reference')
    if ref in fps:fail.append(f'Duplicate footprint reference {ref}')
    fps[ref]=f
    if ref in authorized_holes:
        pads=children(f,'pad')
        if len(pads)!=1:fail.append(f'{ref}: expected exactly one NPTH pad')
        if tuple(map(float,one(f,'at')[1:3]))!=authorized_holes[ref]:fail.append(f'{ref}: unauthorized mounting position')
        for p in pads:
            if p[2:4]!=['np_thru_hole','circle'] or one(p,'drill')[1:]!=['2.7'] or one(p,'at')[1:3]!=['0','0']:
                fail.append(f'{ref}: expected centered circular 2.7 mm NPTH')
            if len(one(p,'net'))>1:fail.append(f'{ref}: mounting hole unexpectedly has a net')
    for p in children(f,'pad'):
        pin=p[1];net=one(p,'net');name=net[2].removeprefix('/') if len(net)>2 else ''
        if pin.startswith('MP') or pin=='':
            mechanical.append({'ref':ref,'pin':pin,'net':name})
            if name:fail.append(f'Unexpected mechanical pad net {ref}.{pin}={name}')
            continue
        padnets.setdefault((ref,pin),[]).append(name)
        if nets.get((ref,pin))!=name:fail.append(f'{ref}.{pin}: expected {nets.get((ref,pin))}, board {name}')
        pad_geometry.append({'ref':ref,'pin':pin,'local_at':one(p,'at')[1:],'size':one(p,'size')[1:],'drill':one(p,'drill')[1:]})
missing=sorted(set(comps)-set(fps));extra=sorted(set(fps)-set(comps)-set(authorized_holes));missingpins=sorted(set(nets)-set(padnets))
if set(fps)&set(authorized_holes) and not set(authorized_holes)<=set(fps):fail.append('Incomplete authorized mounting-hole set')
if missing:fail.append(f'Missing footprints {missing}')
if extra:fail.append(f'Unexpected footprints {extra}')
if missingpins:fail.append(f'Missing electrical pads {missingpins}')
for r,c in comps.items():
    assigned=val(c,'footprint')
    if not assigned:fail.append(f'{r}: schematic footprint unassigned')
    elif r in fps and fps[r][1]!=assigned:fail.append(f'{r}: schematic footprint {assigned}, board footprint {fps[r][1]}')
result={'scope':'pad-net and footprint parity only; not routed connectivity or DRC',
 'netlist_sha256':hashlib.sha256(netpath.read_bytes()).hexdigest(),'board_sha256':hashlib.sha256(boardpath.read_bytes()).hexdigest(),
 'schematic_components':len(comps),'board_footprints':len(fps),'electrical_pads':sum(map(len,padnets.values())),
 'authorized_board_only_mounts':sorted(set(fps)&set(authorized_holes)),
 'mechanical_pads':mechanical,'tracks':len(children(board,'segment')),'vias':len(children(board,'via')),'zones':len(children(board,'zone')),
 'verdict':'FAIL' if fail else 'PASS','failures':fail,'pad_geometry':pad_geometry}
print(json.dumps(result,indent=2));sys.exit(bool(fail))
