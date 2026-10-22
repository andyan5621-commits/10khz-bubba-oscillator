from pathlib import Path
import json,math,heapq,collections
ns={};exec(Path('oscillator-pcb/verification/check_board_parity.py').read_text().split('netpath,boardpath=')[0],ns)
parse,children,one=ns['parse'],ns['children'],ns['one']
p=Path('oscillator-pcb/pcb/routing-candidate.kicad_pcb');b=parse(p.read_text())
names={n[1]:n[2] for n in children(b,'net')}
stats=collections.defaultdict(lambda:collections.defaultdict(float));graphs=collections.defaultdict(lambda:collections.defaultdict(list))
def pt(v):return tuple(round(float(x),6) for x in v)
for s in children(b,'segment'):
    net=one(s,'net')[1];layer=one(s,'layer')[1];a=pt(one(s,'start')[1:]);z=pt(one(s,'end')[1:]);length=math.dist(a,z)
    stats[names[net]][layer]+=length
    a=(*a,layer);z=(*z,layer);graphs[net][a].append((z,length));graphs[net][z].append((a,length))
for v in children(b,'via'):
    net=one(v,'net')[1];pos=pt(one(v,'at')[1:]);a=(*pos,'F.Cu');z=(*pos,'B.Cu')
    graphs[net][a].append((z,0));graphs[net][z].append((a,0))
pads={}
for f in children(b,'footprint'):
    ref=next(p[2] for p in children(f,'property') if p[1]=='Reference');at=list(map(float,one(f,'at')[1:]));angle=math.radians(at[2] if len(at)>2 else 0)
    for pad in children(f,'pad'):
        net=one(pad,'net')
        if len(net)<2:continue
        x,y=map(float,one(pad,'at')[1:3]);pos=pt([at[0]+x*math.cos(angle)+y*math.sin(angle),at[1]-x*math.sin(angle)+y*math.cos(angle)])
        pads[(ref,pad[1])]=(pos,net[1]);
        if pad[2]=='thru_hole':
            a=(*pos,'F.Cu');z=(*pos,'B.Cu');graphs[net[1]][a].append((z,0));graphs[net[1]][z].append((a,0))
def shortest(a,z):
    start,net=pads[a];end,net2=pads[z];assert net==net2
    todo=[(0,(*start,'F.Cu'))];seen=set()
    while todo:
        d,n=heapq.heappop(todo)
        if n in seen:continue
        if n[:2]==end:return d
        seen.add(n)
        for dest,weight in graphs[net][n]:heapq.heappush(todo,(d+weight,dest))
    return None
bp=[]
for i in range(1,5):
    for pin,c in [('8',i+6),('4',i+10)]:bp.append({'from':f'U{i}.{pin}','to':f'C{c}.1' if c<11 else f'C{c}.2','length_mm':shortest((f'U{i}',pin),(f'C{c}','1' if c<11 else '2'))})
print(json.dumps({'source':str(p),'local_bypass_shortest_trace_length_mm':bp,'net_trace_length_by_layer_mm':stats},indent=2))
