from pathlib import Path
import xml.etree.ElementTree as E,collections,json
files=['oscillator-pcb/verification/history/pre-loop-cleanup-front.svg','oscillator-pcb/verification/routed-front.svg']
def copper(p):
 root=E.parse(p).getroot();items=[]
 def walk(e,style):
  style=style|dict(x.strip().split(':',1) for x in e.get('style','').split(';') if ':' in x)
  if len(e)==0 and '#C83434' in [style.get('stroke'),style.get('fill')]:
   attrs={k:v for k,v in e.attrib.items() if k!='style'};items.append(json.dumps([e.tag,attrs,style],sort_keys=True))
  for c in e:walk(c,style)
 walk(root,{})
 return collections.Counter(items)
a,b=map(copper,files);removed=list((a-b).elements());added=list((b-a).elements())
print(json.dumps({'scope':'Native SVG red front-copper geometry comparison against pre-loop-cleanup rendering','removed_primitive_count':len(removed),'added_primitive_count':len(added),'removed':[json.loads(s) for s in removed],'added':[json.loads(s) for s in added]},indent=2))
