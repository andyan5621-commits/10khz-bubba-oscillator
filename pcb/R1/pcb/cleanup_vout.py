from pathlib import Path
import pcbnew as p
import json,hashlib
root=Path(__file__).resolve().parent
b=p.LoadBoard(str(root/'oscillator.kicad_pcb'))
pairs=[((99,100),(102,103)),((102,103),(103,103)),((103,103),(104,104)),((104,104),(104.75,104))]
removed=[];removed_objects=[]
original_length=sum(p.ToMM(t.GetLength()) for t in b.GetTracks() if t.GetNetname()=='/VOUT')
for t in list(b.GetTracks()):
    if isinstance(t,p.PCB_VIA) or t.GetNetname()!='/VOUT':continue
    a=(p.ToMM(t.GetStart().x),p.ToMM(t.GetStart().y));z=(p.ToMM(t.GetEnd().x),p.ToMM(t.GetEnd().y))
    if any({a,z}=={x,y} for x,y in pairs):
        removed.append({'start_mm':a,'end_mm':z,'length_mm':p.ToMM(t.GetLength())});removed_objects.append(t);b.Remove(t)
assert len(removed) in [0,4],removed
if not removed:
    print('VOUT loop already removed; board unchanged.');raise SystemExit(0)
b.BuildConnectivity();filler=p.ZONE_FILLER(b);filler.Fill(b.Zones())
for name in ['oscillator.kicad_pcb','routing-candidate.kicad_pcb']:p.SaveBoard(str(root/name),b)
audit={'reason':'Chief-approved redundant same-net loop removal; no pads or replacement tracks added','removed':removed,'removed_length_mm':sum(x['length_mm'] for x in removed),'vout_total_mm':original_length-sum(x['length_mm'] for x in removed),'board_sha256':hashlib.sha256((root/'oscillator.kicad_pcb').read_bytes()).hexdigest()}
(root/'vout-loop-cleanup.json').write_text(json.dumps(audit,indent=2));print(audit)
