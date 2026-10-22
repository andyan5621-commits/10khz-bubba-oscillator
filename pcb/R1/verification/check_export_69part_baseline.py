"""Independent exported-net checks. Does not import schematic/layout generators.

Usage: python verification/check_export.py schematic/oscillator_modern.net
Expected topology transcribed from original LTspice-generated final netlist;
physical resistor expansion and potentiometer follow confirmed user requirement.
PASS here means electrical capture only, never fabrication/performance approval.
"""
import collections
import hashlib
import json
import math
from pathlib import Path
import re
import sys

def parse(text):
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', text)
    root, stack = [], []
    active = root
    for t in tokens:
        if t == '(':
            child=[]; active.append(child); stack.append(active); active=child
        elif t == ')': active=stack.pop()
        else: active.append(json.loads(t) if t.startswith('"') else t)
    if stack: raise ValueError('unbalanced netlist')
    return root[0]

def children(node, name): return [c for c in node if isinstance(c,list) and c and c[0]==name]
def one(node,name): return next((c for c in children(node,name)), [name])
def scalar(node,name,default=''): return (one(node,name)+[default])[1]
def value(s):
    m=re.fullmatch(r'([\d.]+)([kKmMuUnNpP]?)',s)
    if not m: raise ValueError(s)
    return float(m[1])*{'':1,'k':1e3,'K':1e3,'M':1e6,'m':1e-3,'u':1e-6,'U':1e-6,'n':1e-9,'N':1e-9,'p':1e-12,'P':1e-12}[m[2]]

path=Path(sys.argv[1]); source=path.read_bytes(); doc=parse(source.decode('utf-8-sig'))
components={scalar(c,'ref'):c for c in children(one(doc,'components'),'comp')}
pins={}; net_nodes={}; failures=[]
for n in children(one(doc,'nets'),'net'):
    name=scalar(n,'name').removeprefix('/')
    nodes=[]
    for p in children(n,'node'):
        key=(scalar(p,'ref'),scalar(p,'pin'))
        if key in pins: failures.append(f'Duplicate net assignment: {key}')
        pins[key]=name; nodes.append(key)
    net_nodes[name]=nodes

def require(condition,message):
    if not condition: failures.append(message)
def check(ref,pin,net): require(pins.get((ref,str(pin)))==net,f'{ref}.{pin}: expected {net}; found {pins.get((ref,str(pin)))}')

require(len(components)==69,f'Physical component count {len(components)}, expected69')
resistors={r:c for r,c in components.items() if re.fullmatch(r'R\d+',r)}
require(len(resistors)==44,f'Fixed resistor count {len(resistors)}, expected44')
require({r for r in components if r.startswith('U')}=={'U1','U2','U3','U4'},'Four dual IC references required')

# Physical TI OPA1656IDR D/SOIC pinout:1OUTA,2INA-,3INA+,4V-,5INB+,6INB-,7OUTB,8V+.
amps={
 'U1':{1:'GAIN_OUT',2:'N_INV',3:'GND',5:'KICK',6:'N_STAGE1',7:'N_STAGE1'},
 'U2':{1:'N_STAGE3',2:'N_STAGE3',3:'N_STAGE2',5:'N_STAGE4',6:'N_STAGE5',7:'N_STAGE5'},
 'U3':{1:'N_BUF',2:'N_BUF',3:'VOUT',5:'N_FILT_IN',6:'VFILTERED',7:'VFILTERED'},
 'U4':{1:'N_OUTBUF',2:'N_OUTBUF',3:'VFILTERED',5:'GND',6:'SPARE_FB',7:'SPARE_FB'},
}
for r,mapping in amps.items():
    for p,n in {**mapping,4:'-15V',8:'+15V'}.items(): check(r,p,n)
    require(scalar(components.get(r,[]),'value')=='OPA1656IDR',f'{r}: wrong IC value')
    require(scalar(components.get(r,[]),'footprint')=='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',f'{r}: wrong SOIC footprint')

for r,p,n in [('D1',1,'LIMIT_HI'),('D1',2,'N_INV'),('D2',1,'N_INV'),('D2',2,'LIMIT_LO'),
              ('C15',1,'+15V'),('C15',2,'GND'),('C16',1,'GND'),('C16',2,'-15V'),
              ('J1',1,'+15V'),('J1',2,'GND'),('J1',3,'-15V'),('J2',1,'OUTPUT'),('J2',2,'GND'),
              ('RV1',1,'VFINAL'),('RV1',2,'OUTPUT'),('RV1',3,'GND')]: check(r,p,n)
require(scalar(components.get('RV1',[]),'value')=='10k','RV1 must be10k')
for i,(nets,v) in enumerate([({'KICK','GND'},'10n'),({'N_STAGE2','GND'},'10n'),({'N_STAGE4','GND'},'10n'),({'VOUT','GND'},'10n'),({'N_FILT_IN','GND'},'1n'),({'N_FILT_SUM','VFILTERED'},'68n')],1):
    r=f'C{i}'; require({pins.get((r,'1')),pins.get((r,'2'))}==nets,f'{r}: wrong capacitor nets')
    require(value(scalar(components.get(r,[]),'value','0'))==value(v),f'{r}: wrong capacitance')
for i in range(7,15):
    r=f'C{i}'; require({pins.get((r,'1')),pins.get((r,'2'))}=={'GND','+15V' if i<11 else '-15V'},f'{r}: wrong bypass nets')
    require(math.isclose(value(scalar(components.get(r,[]),'value','0')),1e-7,rel_tol=1e-12),f'{r}: wrong bypass value')

# Every expected series chain must be a unique simple path whose intermediate
# nodes touch exactly two pins, both resistors. This detects branches and omitted
# parts even when equivalent resistance appears correct.
expected=[
 ('R1','GAIN_OUT','KICK',[1000,330,270,47]),
 ('R2','N_STAGE1','N_STAGE2',[1000,330,270,47]),
 ('R3','N_STAGE3','N_STAGE4',[1000,330,270,47]),
 ('R4','N_STAGE5','VOUT',[1000,330,270,47]),
 ('RG','VOUT','N_INV',[10000]),('RF','GAIN_OUT','N_INV',[47000,1000]),
 ('R5','LIMIT_HI','GAIN_OUT',[100000,20000,10000]),
 ('R6','+15V','LIMIT_HI',[300000,20000,4700,200,100]),
 ('R7','GAIN_OUT','LIMIT_LO',[100000,20000,10000]),
 ('R8','LIMIT_LO','-15V',[300000,20000,4700,200,100]),
 ('R9','N_BUF','N_FILT_SUM',[1000,680,220]),
 ('R10','N_FILT_SUM','N_FILT_IN',[1000,680,220]),
 ('R11A','N_OUTBUF','VFINAL',[2000]),('R11B','N_OUTBUF','VFINAL',[100000]),
 ('R12','VFINAL','GND',[1000]),
]
boundaries={n for _,a,b,_ in expected for n in (a,b)}
adj=collections.defaultdict(list)
for r,c in resistors.items():
    a,b=pins.get((r,'1')),pins.get((r,'2'))
    require(a is not None and b is not None,f'{r}: unconnected resistor')
    adj[a].append((r,b));adj[b].append((r,a))
chains=[];seen=set()
for start in sorted(boundaries):
    for ref,nxt in adj[start]:
        if ref in seen: continue
        chain=[ref];seen.add(ref);current=nxt
        while current not in boundaries:
            if len(net_nodes.get(current,[]))!=2 or len(adj[current])!=2:
                failures.append(f'Unexpected intermediate branch/load at {current}');break
            choices=[(r,n) for r,n in adj[current] if r not in seen]
            if len(choices)!=1: failures.append(f'Non-simple resistor path at {current}');break
            r,current=choices[0];chain.append(r);seen.add(r)
        chains.append((frozenset((start,current)),sorted(value(scalar(resistors[r],'value')) for r in chain),chain))
for logical,a,b,vals in expected:
    matches=[c for c in chains if c[0]==frozenset((a,b)) and c[1]==sorted(vals)]
    require(len(matches)==1,f'{logical}: expected {vals} between {a} and {b}; found {[(c[1],c[2]) for c in chains if c[0]==frozenset((a,b))]}')
require(len(chains)==len(expected),f'Expected15 independent resistor paths; found{len(chains)}')
require(seen==set(resistors),f'Untraversed resistor references {sorted(set(resistors)-seen)}')

result={'scope':'electrical capture; NOT fabrication/performance release','netlist':str(path),'sha256':hashlib.sha256(source).hexdigest(),
        'component_count':len(components),'fixed_resistor_count':len(resistors),'net_count':len(net_nodes),
        'verdict':'FAIL' if failures else 'PASS','failures':failures,
        'resistor_chains':[{'ends':sorted(n),'values_ohm':v,'references':r} for n,v,r in chains]}
print(json.dumps(result,indent=2));sys.exit(bool(failures))
