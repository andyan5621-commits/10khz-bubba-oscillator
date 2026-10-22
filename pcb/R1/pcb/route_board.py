"""Deterministic two-layer routing candidate, only after explicit Gate B approval.

KiCad DRC and pad/net parity are authoritative, not the routing grid's estimates.
This script never creates manufacturing output. It preserves a placement baseline.
"""
from pathlib import Path
import argparse, math, heapq, json, time, shutil
import pcbnew as p
from revision_metadata import apply_metadata

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--gate-b-approved',action='store_true');parser.add_argument('--setup-only',action='store_true');args=parser.parse_args()
if not args.gate_b_approved:raise SystemExit('Explicit Gate B approval required')
baseline=ROOT/'placement-baseline.kicad_pcb'
if not baseline.exists():shutil.copy2(ROOT/'oscillator.kicad_pcb',baseline)
b=p.LoadBoard(str(baseline))
mm=p.FromMM
def xy(x,y):return p.VECTOR2I(mm(x),mm(y))
def point(v):return (p.ToMM(v.x),p.ToMM(v.y))

# Mechanical outline revision approved by the chief: 95 x 79 mm.
edges=[]
for item in list(b.GetDrawings()):
    if item.GetLayer()==p.Edge_Cuts:edges.append(item)
    elif isinstance(item,p.PCB_TEXT):
        txt=item.GetText()
        if 'UNROUTED PLACEMENT' in txt:item.SetText('10 kHz OSCILLATOR  |  R1')
        if 'PLACEMENT STUDY -' in txt:item.SetText('ROUTING REVIEW - NOT RELEASED');item.SetPosition(xy(97.5,43))
        if '95 x 70' in txt:item.SetText('95 x 79 mm / 2 layers / 1.6 mm / 35 um Cu');item.SetPosition(xy(97.5,129))
        if 'no tracks' in txt:item.SetText('Gate B approved; routing and manufacturing review still required');item.SetPosition(xy(97.5,132))
        if 'draft 2026' in txt:item.SetText('OPA1656  |  +/-15 V  |  HIGH-Z OUTPUT');item.SetPosition(xy(97.5,123.5))
for s,(x1,y1,x2,y2) in zip(edges,[(50,47,145,47),(145,47,145,126),(145,126,50,126),(50,126,50,47)]):
    s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(xy(x1,y1));s.SetEnd(xy(x2,y2));s.SetWidth(mm(.05));s.SetLayer(p.Edge_Cuts)
mounts=[(53.5,50.5),(141.5,50.5),(53.5,122.5),(141.5,122.5)]
lib=Path(r'C:\Program Files\KiCad\9.0\share\kicad\footprints')
for i,(x,y) in enumerate(mounts,1):
    f=p.FootprintLoad(str(lib/'MountingHole.pretty'),'MountingHole_2.7mm_M2.5');f.SetReference(f'H{i}');f.SetValue('M2.5 / 2.7 mm NPTH');f.SetPosition(xy(x,y));f.SetFPID(p.LIB_ID('MountingHole','MountingHole_2.7mm_M2.5'));f.SetAttributes(p.FP_BOARD_ONLY|p.FP_EXCLUDE_FROM_BOM|p.FP_EXCLUDE_FROM_POS_FILES);f.Value().SetVisible(False);f.Reference().SetVisible(False);b.Add(f)

# Fabricator-specific refinements: preserve 0.25 mm copper spacing and exposed vias.
ds=b.GetDesignSettings();ds.m_HoleClearance=mm(.30);ds.m_HoleToHoleMin=mm(.30);ds.m_SolderMaskExpansion=mm(.05);ds.m_SolderMaskMinWidth=mm(.10)
for f in b.GetFootprints():
    if f.GetReference()=='D2':f.Reference().SetPosition(xy(64.5,81))
    for item in [f.Reference(),f.Value(),*list(f.GraphicalItems())]:
        if item.GetLayer() in [p.F_SilkS,p.B_SilkS]:
            if isinstance(item,p.PCB_TEXT):item.SetTextThickness(mm(.15));item.SetTextSize(xy(max(.8,p.ToMM(item.GetTextSize().x)),max(.8,p.ToMM(item.GetTextSize().y))))
            elif hasattr(item,'SetWidth'):item.SetWidth(max(mm(.15),item.GetWidth()))
for item in b.GetDrawings():
    if item.GetLayer() in [p.F_SilkS,p.B_SilkS] and isinstance(item,p.PCB_TEXT):item.SetTextThickness(mm(.15))

def polyzone(points,layers,keepout=False):
    z=p.ZONE(b);ls=p.LSET()
    for layer in layers:ls.AddLayer(layer)
    z.SetLayerSet(ls);z.SetIsRuleArea(keepout)
    out=z.Outline();out.NewOutline()
    for x,y in points:out.Append(mm(x),mm(y))
    b.Add(z);return z
for x,y in mounts:
    z=polyzone([(x+3.05*math.cos(i*math.tau/48),y+3.05*math.sin(i*math.tau/48)) for i in range(48)],[p.F_Cu,p.B_Cu],True)
    z.SetDoNotAllowCopperPour(True);z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowPads(False);z.SetDoNotAllowFootprints(False)

if args.setup_only:
    p.SaveBoard(str(ROOT/'routing-candidate.kicad_pcb'),b);raise SystemExit('Mechanical setup saved; no routing')

# Raster obstacles include maximum proposed routing/via radius and a numerical margin.
STEP=.25;OX=50;OY=47;NX=381;NY=317;N=NX*NY
occ=[[0]*N for _ in range(2)];FIXED=1<<63
def index(x,y):return y*NX+x
def coord(i):return (OX+(i%NX)*STEP,OY+(i//NX)*STEP)
def grid(x,y):return (round((x-OX)/STEP),round((y-OY)/STEP))
def paint_rect(cx,cy,hx,hy,angle,mask,layers):
    rad=math.radians(angle);c,s=math.cos(rad),math.sin(rad);rx=abs(hx*c)+abs(hy*s);ry=abs(hx*s)+abs(hy*c)
    x0,y0=grid(cx-rx-STEP,cy-ry-STEP);x1,y1=grid(cx+rx+STEP,cy+ry+STEP)
    for gy in range(max(0,y0),min(NY-1,y1)+1):
        py=OY+gy*STEP-cy
        for gx in range(max(0,x0),min(NX-1,x1)+1):
            px=OX+gx*STEP-cx
            if abs(px*c-py*s)<=hx and abs(px*s+py*c)<=hy:
                k=index(gx,gy)
                for layer in layers:occ[layer][k]|=mask
def paint_capsule(a,c,r,mask,layers):
    ax,ay=a;cx,cy=c;vx=cx-ax;vy=cy-ay;den=vx*vx+vy*vy
    x0,y0=grid(min(ax,cx)-r-STEP,min(ay,cy)-r-STEP);x1,y1=grid(max(ax,cx)+r+STEP,max(ay,cy)+r+STEP)
    for gy in range(max(0,y0),min(NY-1,y1)+1):
        py=OY+gy*STEP
        for gx in range(max(0,x0),min(NX-1,x1)+1):
            px=OX+gx*STEP;t=max(0,min(1,((px-ax)*vx+(py-ay)*vy)/den)) if den else 0
            if (px-ax-t*vx)**2+(py-ay-t*vy)**2<=r*r:
                k=index(gx,gy)
                for layer in layers:occ[layer][k]|=mask

pads={};netpads={};drilled=[];plated=[]
for f in b.GetFootprints():
    for pad in f.Pads():
        x,y=point(pad.GetPosition());w,h=point(pad.GetSize());net=pad.GetNetCode();mask=1<<net if net else FIXED
        layers=[0,1] if pad.GetAttribute()!=p.PAD_ATTRIB_SMD else [0]
        if len(layers)==2:
            drilled.append(((x,y),max(point(pad.GetDrillSize()))/2))
            if net:plated.append(((x,y),min(w,h)/2,net))
        if f.GetReference().startswith('H'):paint_capsule((x,y),(x,y),3.05+.33,FIXED,layers);continue
        extra=.58
        if pad.GetShape()==p.PAD_SHAPE_CIRCLE:paint_capsule((x,y),(x,y),w/2+extra,mask,layers)
        else:paint_rect(x,y,w/2+extra,h/2+extra,pad.GetOrientationDegrees(),mask,layers)
        if net:
            record={'ref':f.GetReference(),'pin':pad.GetNumber(),'xy':(x,y),'net':net,'layers':layers}
            pads[(f.GetReference(),pad.GetNumber())]=record;netpads.setdefault(net,[]).append(record)
for layer in range(2):
    for gy in range(NY):
        for gx in range(NX):
            x=OX+gx*STEP;y=OY+gy*STEP
            if x<50.8 or x>144.2 or y<47.8 or y>125.2:occ[layer][index(gx,gy)]|=FIXED

tracks=[];vias=[];route_log=[];moves=[(1,0,1),(-1,0,1),(0,1,1),(0,-1,1),(1,1,1.414214),(1,-1,1.414214),(-1,1,1.414214),(-1,-1,1.414214)]
def existing_transition(at,net):
    return any(n==net and math.dist(at,center)<=r+.0001 for center,r,n in plated) or any(v.GetNetCode()==net and math.dist(at,point(v.GetPosition()))<.0001 for v in vias)
def via_allowed(at,net):
    if existing_transition(at,net):return True
    return all(math.dist(at,center)>=radius+.15+.33 for center,radius in drilled)
def addtrack(a,c,layer,net,width):
    if math.dist(a,c)<.00001:return
    t=p.PCB_TRACK(b);t.SetStart(xy(*a));t.SetEnd(xy(*c));t.SetLayer(p.F_Cu if layer==0 else p.B_Cu);t.SetWidth(mm(width));t.SetNetCode(net);b.Add(t);tracks.append(t)
    paint_capsule(a,c,width/2+.25+.25+.08,1<<net,[layer])
def addvia(at,net):
    # No tenting; the PCB project's solder-mask rules provide normal expansion.
    if existing_transition(at,net):return
    if not via_allowed(at,net):raise RuntimeError(f'Via/hole clearance at {at}')
    v=p.PCB_VIA(b);v.SetPosition(xy(*at));v.SetWidth(mm(.6));v.SetDrill(mm(.3));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNetCode(net);v.SetFrontTentingMode(p.TENTING_MODE_NOT_TENTED);v.SetBackTentingMode(p.TENTING_MODE_NOT_TENTED);b.Add(v);vias.append(v);paint_capsule(at,at,.88,1<<net,[0,1])
    drilled.append((at,.15))

def astar(a,c,net,top_only=False):
    sx,sy=grid(*a);tx,ty=grid(*c);start=index(sx,sy);target=index(tx,ty);foreign=~(1<<net)
    def free(layer,k):return not(occ[layer][k]&foreign)
    if not free(0,start) or not free(0,target):return None,'endpoint blocked'
    def h(k):
        gx,gy=k%NX,k//NX;dx,dy=abs(gx-tx),abs(gy-ty);return max(dx,dy)+.414214*min(dx,dy)
    costs={start:0};prev={};heap=[(h(start),0,start)];closed=set();visited=0
    while heap:
        _,cost,state=heapq.heappop(heap)
        if state in closed:continue
        layer,k=divmod(state,N)
        if k==target and layer==0:
            path=[state]
            while path[-1]!=start:path.append(prev[path[-1]])
            return path[::-1],visited
        closed.add(state);visited+=1
        if visited>180000:return None,'search limit'
        gx,gy=k%NX,k//NX
        for dx,dy,length in moves:
            xx,yy=gx+dx,gy+dy
            if xx<1 or xx>=NX-1 or yy<1 or yy>=NY-1:continue
            nk=index(xx,yy);ns=layer*N+nk
            if ns in closed or not free(layer,nk):continue
            if dx and dy and (not free(layer,index(gx+dx,gy)) or not free(layer,index(gx,gy+dy))):continue
            ng=cost+length*(1 if layer==0 else 4)
            if ng<costs.get(ns,float('inf')):costs[ns]=ng;prev[ns]=state;heapq.heappush(heap,(ng+h(nk),ng,ns))
        if not top_only and free(1-layer,k) and via_allowed(coord(k),net):
            ns=(1-layer)*N+k;ng=cost+35
            if ns not in closed and ng<costs.get(ns,float('inf')):costs[ns]=ng;prev[ns]=state;heapq.heappush(heap,(ng+h(k),ng,ns))
    return None,'no path'

def route(a,c,net,width=.3,top_only=False,label=''):
    path,detail=astar(a,c,net,top_only)
    if path is None:
        route_log.append({'net':net,'label':label,'from':a,'to':c,'status':'FAILED','reason':detail});return False
    # Compress collinear grid runs; exact pad-centre tails remain inside the pad.
    first=coord(path[0]%N);addtrack(a,first,0,net,width)
    segment_start=first;last=first;layer=0;direction=None
    for state in path[1:]:
        nl,k=divmod(state,N);now=coord(k)
        if nl!=layer:
            addtrack(segment_start,last,layer,net,width);addvia(last,net);layer=nl;segment_start=last;direction=None;continue
        d=(round((now[0]-last[0])/STEP),round((now[1]-last[1])/STEP))
        if direction is not None and d!=direction:addtrack(segment_start,last,layer,net,width);segment_start=last
        direction=d;last=now
    addtrack(segment_start,last,layer,net,width);addtrack(last,c,0,net,width)
    route_log.append({'net':net,'label':label,'from':a,'to':c,'status':'ROUTED','grid_visits':detail});return True

netnames={n:b.FindNet(n).GetNetname() for n in netpads};gnd=next(n for n,name in netnames.items() if name=='/GND')
done_pairs=set()
# First route the short local supply loops, before larger rail distribution branches.
for i in range(1,5):
    for upin,cref,cpin in [('8',f'C{6+i}','1'),('4',f'C{10+i}','2')]:
        a=pads[(f'U{i}',upin)];c=pads[(cref,cpin)]
        ok=route(a['xy'],c['xy'],a['net'],.3,True,f'local bypass U{i}.{upin}-{cref}.{cpin}')
        if not ok:raise RuntimeError(route_log[-1])
        done_pairs.add(frozenset([(a['ref'],a['pin']),(c['ref'],c['pin'])]))

# Reserve direct ground escapes before signal routing crowds the SOIC supply/input side.
ground_done=set()
for key,at in [(('U1','3'),(68.25,72.75)),(('U4','5'),(127.75,83)),(('TP2','1'),(82.5,114))]:
    a=pads[key]
    if route(a['xy'],at,gnd,.3,True,f'early ground via {key[0]}.{key[1]}'):
        addvia(at,gnd);ground_done.add(key)

def priority(net):
    refs={(r['ref'],r['pin']) for r in netpads[net]};name=netnames[net]
    if ('U1','2') in refs:return (0,net)
    if ('R14','2') in refs:return (1,net)
    if ('D1','1') in refs or ('D2','2') in refs:return (2,net)
    if name in ['/+15V','/-15V']:return (10,net)
    if len(refs)==2:return (3,net)
    return (5,len(refs),net)
failed=[]
for net in sorted([n for n in netpads if n!=gnd],key=priority):
    group=netpads[net];tree=[group[0]];remaining=group[1:];israil=netnames[net] in ['/+15V','/-15V']
    while remaining:
        dist,ia,ic=min((math.dist(a['xy'],c['xy']),ia,ic) for ia,a in enumerate(tree) for ic,c in enumerate(remaining))
        a=tree[ia];c=remaining.pop(ic);pair=frozenset([(a['ref'],a['pin']),(c['ref'],c['pin'])]);tree.append(c)
        if pair in done_pairs:continue
        ok=route(a['xy'],c['xy'],net,.5 if israil else .3,priority(net)[0]<=2,f"{a['ref']}.{a['pin']}-{c['ref']}.{c['pin']}")
        if not ok:failed.append(route_log[-1])
    print(netnames[net],len(group),'pads; failures',len(failed),flush=True)

# Give every SMD ground pin a nearby via; THT grounded pads already reach B.Cu.
for pad in netpads[gnd]:
    if len(pad['layers'])==2:continue
    if (pad['ref'],pad['pin']) in ground_done:continue
    ax,ay=pad['xy'];candidates=[];foreign=~(1<<gnd)
    for radius in [1.25,1.5,2.0,2.5,3.0,4.0]:
        for angle in range(0,360,45):
            gx,gy=grid(ax+radius*math.cos(math.radians(angle)),ay+radius*math.sin(math.radians(angle)));k=index(gx,gy)
            if 0<=gx<NX and 0<=gy<NY and not (occ[0][k]&foreign or occ[1][k]&foreign) and via_allowed(coord(k),gnd):candidates.append((math.dist((ax,ay),coord(k)),coord(k)))
        if candidates:break
    connected=False
    for _,at in sorted(candidates):
        if route((ax,ay),at,gnd,.3,True,f'ground via {pad["ref"]}.{pad["pin"]}'):
            addvia(at,gnd);connected=True;break
    if not connected:failed.append({'label':f'ground via {pad["ref"]}.{pad["pin"]}','status':'FAILED'})

# Continuous common-ground plane; no split analog islands. Keep screws clear.
z=polyzone([(50.5,47.5),(144.5,47.5),(144.5,125.5),(50.5,125.5)],[p.B_Cu]);z.SetNetCode(gnd);z.SetLocalClearance(mm(.25));z.SetThermalReliefGap(mm(.3));z.SetThermalReliefSpokeWidth(mm(.35));z.SetPadConnection(p.ZONE_CONNECTION_THERMAL);z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
filler=p.ZONE_FILLER(b);filler.Fill(b.Zones())
p.SaveBoard(str(ROOT/'routing-candidate.kicad_pcb'),b)
apply_metadata(ROOT/'routing-candidate.kicad_pcb')
(ROOT/'routing-log.json').write_text(json.dumps({'status':'CANDIDATE_REQUIRES_NATIVE_DRC','board_size_mm':[95,79],'mounting_holes_mm':mounts,'track_segments':len(tracks),'vias':len(vias),'failed':failed,'routes':route_log},indent=2))
print('Saved candidate:',len(tracks),'tracks',len(vias),'vias',len(failed),'failed routes',flush=True)
