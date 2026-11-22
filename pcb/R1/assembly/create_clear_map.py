"""Create an assembly-only map from frozen R1 pads; never edit CAD."""
from pathlib import Path
import csv, math, re, json, hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Rectangle
from matplotlib.backends.backend_pdf import PdfPages

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assembly/drawings/clear-map'
OUT.mkdir(parents=True,exist_ok=True)
SOURCE=ROOT/'fabrication/review-packages/R1-review-03/source/oscillator.kicad_pcb'
ns={}
exec((ROOT/'verification/check_board_parity.py').read_text().split('netpath,boardpath=')[0],ns)
parse,children,one,val=[ns[k] for k in ('parse','children','one','val')]
board=parse(SOURCE.read_text(encoding='utf-8'))
bom={r['Reference']:r for r in csv.DictReader((ROOT/'bom/per-component.csv').open(encoding='utf-8-sig'))}
parts={}
for f in children(board,'footprint'):
    props={p[1]:p[2] for p in children(f,'property')}
    r=props['Reference'];at=one(f,'at')
    parts[r]={'f':f,'x':float(at[1])-50,'y':float(at[2])-47,'a':float(at[3]) if len(at)>3 else 0,'v':props.get('Value','')}
COLORS=['#007c91','#9a3e00','#7046ac','#236c35','#b32957']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'pdf.fonttype':42,'svg.fonttype':'none'})

def transform(p,x,y):
    a=math.radians(p['a'])
    return p['x']+x*math.cos(a)+y*math.sin(a),p['y']-x*math.sin(a)+y*math.cos(a)

def draw(ax,focus=None,outline=True,context=True):
    if outline:ax.add_patch(Rectangle((0,0),95,79,facecolor='#f5f8fa',edgecolor='#344b5a',lw=1.3,zorder=0))
    for r,p in parts.items():
        f=p['f'];active=focus is None or r in focus
        if not active and not context:continue
        edge='#273b48' if active else '#c8d1d7'
        # Actual native fabrication body outlines, without the ambiguous silk labels.
        for kind in ['fp_line','fp_rect','fp_circle']:
            for q in children(f,kind):
                if val(q,'layer')!='F.Fab':continue
                if kind=='fp_line':
                    s=transform(p,*map(float,one(q,'start')[1:3]));e=transform(p,*map(float,one(q,'end')[1:3]))
                    ax.plot([s[0],e[0]],[s[1],e[1]],color=edge,lw=.65,zorder=2)
                elif kind=='fp_rect':
                    x1,y1=map(float,one(q,'start')[1:3]);x2,y2=map(float,one(q,'end')[1:3])
                    ax.add_patch(Polygon([transform(p,x,y) for x,y in [(x1,y1),(x2,y1),(x2,y2),(x1,y2)]],closed=True,fill=False,ec=edge,lw=.65,zorder=2))
                else:
                    cx,cy=map(float,one(q,'center')[1:3]);ex,ey=map(float,one(q,'end')[1:3])
                    ax.add_patch(Circle(transform(p,cx,cy),math.hypot(ex-cx,ey-cy),fill=False,ec=edge,lw=.65,zorder=2))
        for pad in children(f,'pad'):
            pa=one(pad,'at');x,y=map(float,pa[1:3]);cx,cy=transform(p,x,y)
            w,h=map(float,one(pad,'size')[1:3]);angle=float(pa[3]) if len(pa)>3 else p['a']
            color='#e3b75b' if active else '#e4e8eb'
            if pad[3]=='circle':ax.add_patch(Circle((cx,cy),w/2,fc=color,ec=edge,lw=.45,zorder=3))
            else:
                a=math.radians(angle)
                pts=[(cx+dx*math.cos(a)+dy*math.sin(a),cy-dx*math.sin(a)+dy*math.cos(a)) for dx,dy in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]]
                ax.add_patch(Polygon(pts,fc=color,ec=edge,lw=.45,zorder=3))
            d=one(pad,'drill')
            if len(d)>1:
                size=float(d[2] if d[1]=='oval' else d[1])
                ax.add_patch(Circle((cx,cy),size/2,fc='white',ec=edge,lw=.35,zorder=4))
        if re.fullmatch(r'R\d+',r):
            ax.add_patch(Polygon([transform(p,x,y) for x,y in [(-.9,-.55),(.9,-.55),(.9,.55),(-.9,.55)]],fc='#dde8ee' if active else '#eef1f3',ec=edge,lw=.65,zorder=5))
    ax.set_aspect('equal');ax.axis('off')

def pretty(v):
    return {'1k':'1 kOhm','2k':'2 kOhm','4.7k':'4.7 kOhm','10k':'10 kOhm','20k':'20 kOhm','47k':'47 kOhm','100k':'100 kOhm','300k':'300 kOhm','10n':'10 nF','1n':'1 nF','68n':'68 nF','100n':'100 nF','10u 50V':'10 uF / 50 V'}.get(v,v+' Ohm' if v.isdigit() else v)

def label(r):
    if r.startswith('U'):return r+'  OPA1656'
    if r=='J1':return 'J1  +15V / GND / -15V'
    if r=='J2':return 'J2  BNC output'
    if r=='RV1':return 'RV1  10 kOhm pot'
    return r+'  '+pretty(parts[r]['v'])

def callouts(ax,refs,left,right,ylo,yhi,split):
    for side in [0,1]:
        selected=sorted([r for r in refs if (parts[r]['x']<=split)==(side==0)],key=lambda r:(parts[r]['y'],parts[r]['x']))
        ys=[(ylo+yhi)/2] if len(selected)==1 else [ylo+(yhi-ylo)*i/(len(selected)-1) for i in range(len(selected))]
        for i,(r,y) in enumerate(zip(selected,ys)):
            p=parts[r];c=COLORS[i%len(COLORS)];x=left if side==0 else right
            ax.annotate(label(r),xy=(p['x'],p['y']),xytext=(x,y),ha='right' if side==0 else 'left',va='center',fontsize=10.5,fontweight='bold',color=c,
                bbox={'boxstyle':'round,pad=.22','fc':'white','ec':'none'},arrowprops={'arrowstyle':'-','color':c,'lw':1.05,'shrinkA':3,'shrinkB':0},zorder=10)
            ax.plot(p['x'],p['y'],'o',ms=3,color=c,zorder=11)

def page(title,sub,num):
    fig=plt.figure(figsize=(11.7,8.3),facecolor='white')
    fig.text(.045,.948,title,size=21,weight='bold',color='#183d50')
    fig.text(.045,.907,sub,size=10,color='#485b67')
    fig.text(.045,.031,'R1 | COMPONENT SIDE | Board title at top, BNC on right | Assembly map only; not to scale',size=8,color='#596d78')
    fig.text(.955,.031,str(num)+' / 6',ha='right',size=9,color='#596d78')
    return fig

res={r for r in parts if re.fullmatch(r'R\d+',r)}
A={r for r in res if parts[r]['x']<23}
B={r for r in res if re.fullmatch(r'R[1-4]0[1-4]',r)}
C=res-A-B
assert len(res)==44 and len(A)==19 and len(B)==16 and len(C)==9
covered=set()
pages=[]

fig=page('Clear component map - released R1','Choose the matching detail page. New labels point to pads; do not infer positions from the printed silkscreen.',1)
ax=fig.add_axes([.18,.105,.64,.76]);draw(ax)
for x,y,w,h,c,title in [(1,5,23,43,'#007c91','A - PAGE 2'),(24,8,33,54,'#7046ac','B - PAGE 3'),(59,31,22,29,'#b32957','C - PAGE 4')]:
    ax.add_patch(Rectangle((x,y),w,h,fill=False,ec=c,lw=2,ls='--',zorder=8));ax.text(x,y-1.5,title,color=c,fontsize=10,weight='bold',zorder=9)
ax.text(47.5,3.5,'10 kHz OSCILLATOR | R1',ha='center',size=10,weight='bold')
for r,xy in [('J1',(8,71)),('J2',(99,60)),('RV1',(79,7)),('C15',(23,58)),('C16',(32,58)),('TP1',(25,72)),('TP2',(31,72)),('TP3',(37,72))]:
    ax.annotate(r,xy=(parts[r]['x'],parts[r]['y']),xytext=xy,ha='center',size=9,weight='bold',arrowprops={'arrowstyle':'-','lw':.7},zorder=9)
ax.set_xlim(-5,119);ax.set_ylim(83,-3)
fig.text(.045,.085,'PAGE 5: capacitors, diodes, op-amps and connectors.  Gold = pad; white = hole; pale outlines = component bodies.',size=9)
pages.append(('01-overview',fig))

fig=page('A - Left-side resistor detail','Follow each colored line to its dot. R703 is vertical; R702 and R701 are the two horizontal parts beside it.',2)
ax=fig.add_axes([.06,.12,.88,.74]);draw(ax,A)
callouts(ax,A,-2,27,5,46,10.5)
ax.set_xlim(-27,53);ax.set_ylim(49,2)
fig.text(.06,.081,'R703 = 10 kOhm     R702 = 20 kOhm     R701 = 100 kOhm     R801 = 300 kOhm',size=11,weight='bold',color='#9a3e00')
pages.append(('02-left-resistors',fig));covered|=A

fig=page('B - Four timing-resistor chains','Each chain is 1 kOhm + 330 Ohm + 270 Ohm + 47 Ohm. The pad layout is shown in its actual top-view orientation.',3)
for i,group in enumerate([[f'R{n}0{j}' for j in range(1,5)] for n in range(1,5)]):
    ax=fig.add_axes([.05+(i%2)*.48,.51-(i//2)*.37,.44,.31]);draw(ax,set(group),False,False)
    xs=[parts[r]['x'] for r in group];yy=parts[group[0]]['y']
    for j,r in enumerate(group):
        p=parts[r];ax.annotate(r+'\n'+pretty(p['v']),xy=(p['x'],p['y']),xytext=(p['x'],yy-4),ha='center',va='bottom',fontsize=9,weight='bold',color=COLORS[j],arrowprops={'arrowstyle':'-','color':COLORS[j],'lw':1},zorder=10)
    ax.text(sum(xs)/4,yy+4,' + '.join(group),ha='center',size=10,color='#485b67')
    ax.set_xlim(min(xs)-3,max(xs)+3);ax.set_ylim(yy+6,yy-9)
pages.append(('03-timing-chains',fig));covered|=B

fig=page('C - Filter and output resistors','R11 takes 2 kOhm. R16 takes 100 kOhm; the board connects them in parallel. Neither is a 1.961 kOhm part.',4)
ax=fig.add_axes([.07,.12,.86,.74]);draw(ax,C)
callouts(ax,C,55,83,36,56,72)
ax.set_xlim(30,113);ax.set_ylim(62,28)
pages.append(('04-output-resistors',fig));covered|=C

fig=page('Remaining components - exact pad locations','Non-polarized: C1-C14. Pin 1: upper-left on U1-U4. D1 stripe up; D2 stripe right. C15/C16 positive lead left.',5)
refs={r for r in parts if r.startswith(('C','D','U','J','RV'))}
ax=fig.add_axes([.025,.11,.95,.75]);draw(ax,refs)
callouts(ax,refs,-5,101,5,74,48)
for r in ['TP1','TP2','TP3']:
    p=parts[r];ax.text(p['x'],p['y']+3,r,ha='center',size=8,weight='bold')
ax.set_xlim(-42,140);ax.set_ylim(82,-2)
fig.text(.045,.078,'C15: + to +15 V, - to GND.    C16: + to GND, - to -15 V.    TP pads require no purchased component.',size=10,weight='bold')
pages.append(('05-other-components',fig))

fig=page('Test points - where to place the probe','These are exposed PCB pads. No test-point hardware is required. Use TP2 for the circuit-ground reference.',6)
ax=fig.add_axes([.025,.11,.95,.75]);tps={r for r in parts if r.startswith('TP')};draw(ax,tps)
callouts(ax,tps,-5,101,23,69,45)
ax.set_xlim(-42,140);ax.set_ylim(82,-2)
ax.text(47.5,4,'10 kHz OSCILLATOR | R1',ha='center',size=9,weight='bold')
fig.text(.045,.078,'Keep power disconnected during soldering. Resistance/continuity measurements are made with power removed.',size=10)
pages.append(('06-test-points',fig))

assert covered==res
for r in res:
    assert parts[r]['v']==bom[r]['Value'],r
pdfpath=OUT/'R1-clear-component-map.pdf'
with PdfPages(pdfpath) as pdf:
    for name,fig in pages:
        pdf.savefig(fig)
        fig.savefig(OUT/(name+'.png'),dpi=180)
        fig.savefig(OUT/(name+'.svg'))
        plt.close(fig)
audit={'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'fixed_resistors_covered':len(covered),'resistor_bom_values_match':True,'components_on_last_page':len(refs),'board_or_manufacturing_files_modified':False}
(OUT/'map-provenance.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
print(json.dumps(audit,indent=2))
