from pathlib import Path
import json
ns={};exec(Path('oscillator-pcb/verification/check_board_parity.py').read_text().split('netpath,boardpath=')[0],ns);parse,c,o=ns['parse'],ns['children'],ns['one']
base=Path('oscillator-pcb/pcb/Oscillator.pretty')
cases=[('C7',base/'C_KEMET_C315C104K5R5TA_P2.54.kicad_mod',base/'C_KEMET_C315_P2.54_RoutedSilk.kicad_mod'),('U3',Path('C:/Program Files/KiCad/9.0/share/kicad/footprints/Package_SO.pretty/SOIC-8_3.9x4.9mm_P1.27mm.kicad_mod'),base/'SOIC-8_3.9x4.9mm_P1.27mm_RoutedSilk.kicad_mod')]
def normal(n):
 if not isinstance(n,list):
  try:return round(float(n),9)
  except (ValueError,TypeError):return 'solid' if n=='default' else n
 if n and n[0]=='fill' and n[1] in ['none','no']:return ['fill','no']
 return [normal(x) for x in n if not(isinstance(x,list) and x and x[0] in ['uuid','net','pinfunction','pintype'] or isinstance(x,list) and x==['remove_unused_layers','no'])]
results=[]
for ref,a,z in cases:
 a=parse(a.read_text());z=parse(z.read_text());pa={p[1]:normal(p) for p in c(a,'pad')};pz={p[1]:normal(p) for p in c(z,'pad')}
 dif=[{'pad':p,'before':pa[p],'after':pz.get(p)} for p in pa if pa[p]!=pz.get(p)]
 ga=[normal(g) for g in a if isinstance(g,list) and g[0].startswith('fp_') and g[0]!='fp_text'];gz=[normal(g) for g in z if isinstance(g,list) and g[0].startswith('fp_') and g[0]!='fp_text']
 ga.sort(key=lambda x:(o(x,'layer')[1],x[0],str(o(x,'start'))));gz.sort(key=lambda x:(o(x,'layer')[1],x[0],str(o(x,'start'))))
 changes=[{'before':g,'after':h} for g,h in zip(ga,gz) if g!=h]
 non_silk_equal=[g for g in ga if o(g,'layer')[1]!='F.SilkS']==[g for g in gz if o(g,'layer')[1]!='F.SilkS']
 results.append({'reference':ref,'non_silk_graphics_equal':non_silk_equal,'pad_geometry_equal':pa==pz,'pad_differences':dif,'graphic_count_before':len(ga),'graphic_count_after':len(gz),'graphic_changes':changes})
print(json.dumps(results,indent=2))
assert all(r['pad_geometry_equal'] and r['non_silk_graphics_equal'] for r in results)
