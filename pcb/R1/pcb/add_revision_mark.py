from pathlib import Path
import hashlib,json
import pcbnew as p
from revision_metadata import apply_metadata
root=Path(__file__).resolve().parent
b=p.LoadBoard(str(root/'oscillator.kicad_pcb'))
def geometry(board):
    return {
        'pads':sorted((f.GetReference(),d.GetNumber(),d.GetPosition().x,d.GetPosition().y,d.GetSize().x,d.GetSize().y,d.GetDrillSize().x,d.GetDrillSize().y,d.GetNetname()) for f in board.GetFootprints() for d in f.Pads()),
        'tracks':sorted((t.m_Uuid.AsString(),t.GetStart().x,t.GetStart().y,t.GetEnd().x,t.GetEnd().y,t.GetWidth(p.F_Cu) if isinstance(t,p.PCB_VIA) else t.GetWidth(),t.GetLayer(),t.GetNetname()) for t in board.GetTracks()),
        'placement':sorted((f.GetReference(),f.GetPosition().x,f.GetPosition().y,f.GetOrientationDegrees()) for f in board.GetFootprints())}
before=geometry(b);changed=0
for item in b.GetDrawings():
    if isinstance(item,p.PCB_TEXT) and item.GetLayer()==p.F_SilkS and item.GetText().startswith('10 kHz OSCILLATOR'):
        item.SetText('10 kHz OSCILLATOR  |  R1');changed+=1
assert changed==1,changed
for name in ['oscillator.kicad_pcb','routing-candidate.kicad_pcb']:
    p.SaveBoard(str(root/name),b);apply_metadata(root/name)
after=geometry(p.LoadBoard(str(root/'oscillator.kicad_pcb')))
assert before==after
digest=hashlib.sha256((root/'oscillator.kicad_pcb').read_bytes()).hexdigest()
audit={'board_sha256':digest,'revision_silkscreen':'10 kHz OSCILLATOR  |  R1','title_revision':'R1','finish':'ENIG','nominal_stackup_mm':{'F.Mask':.01,'F.Cu':.035,'FR4':1.51,'B.Cu':.035,'B.Mask':.01},'pads_tracks_placement_unchanged':before==after}
(root/'revision-mark-audit.json').write_text(json.dumps(audit,indent=2))
fab=json.loads((root/'fabrication-geometry-audit.json').read_text());fab['board_sha256']=digest;(root/'fabrication-geometry-audit.json').write_text(json.dumps(fab,indent=2))
print(audit)
