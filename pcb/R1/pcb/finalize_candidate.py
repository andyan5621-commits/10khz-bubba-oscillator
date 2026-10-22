from pathlib import Path
import json, shutil, hashlib
import pcbnew as p
from revision_metadata import apply_metadata
root=Path(__file__).resolve().parent
path=root/'routing-candidate.kicad_pcb';b=p.LoadBoard(str(path));s=b.GetDesignSettings()
for item in b.GetDrawings():
    if isinstance(item,p.PCB_TEXT) and item.GetLayer()==p.F_SilkS and item.GetText().startswith('10 kHz OSCILLATOR'):
        item.SetText('10 kHz OSCILLATOR  |  R1')
s.m_HoleClearance=p.FromMM(.30);s.m_HoleToHoleMin=p.FromMM(.30);s.m_SolderMaskExpansion=p.FromMM(.05);s.m_SolderMaskMinWidth=p.FromMM(.10)
for t in b.GetTracks():
    if isinstance(t,p.PCB_VIA):t.SetFrontTentingMode(p.TENTING_MODE_NOT_TENTED);t.SetBackTentingMode(p.TENTING_MODE_NOT_TENTED)
for f in b.GetFootprints():
    ref=f.GetReference()
    if ref=='R12':f.Reference().SetPosition(p.VECTOR2I(p.FromMM(129),p.FromMM(95)))
    if ref=='R702':f.Reference().SetPosition(p.VECTOR2I(p.FromMM(57),p.FromMM(70.9)));f.Reference().SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T))
    if ref=='R901':f.Reference().SetPosition(p.VECTOR2I(p.FromMM(127),p.FromMM(85.05)));f.Reference().SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T))
    for item in f.GraphicalItems():
        if not isinstance(item,p.PCB_SHAPE) or item.GetLayer()!=p.F_SilkS:continue
        a=item.GetStart();c=item.GetEnd()
        if ref=='C7' and abs(p.ToMM(a.y)-70.17)<.01 and abs(p.ToMM(c.y)-70.17)<.01:item.SetEnd(p.VECTOR2I(p.FromMM(75.35),p.FromMM(70.17)))
        if ref=='U3' and abs(p.ToMM(a.y)-92.56)<.01 and abs(p.ToMM(c.y)-92.56)<.01:item.SetEnd(p.VECTOR2I(p.FromMM(107.2),p.FromMM(92.56)))
for old,new in [((76,71),(76,70)),((106.5,93.5),(106.5,92.25))]:
    oldpos=p.VECTOR2I(p.FromMM(old[0]),p.FromMM(old[1]));newpos=p.VECTOR2I(p.FromMM(new[0]),p.FromMM(new[1]))
    for t in b.GetTracks():
        if isinstance(t,p.PCB_VIA):
            if t.GetPosition()==oldpos:t.SetPosition(newpos)
        else:
            if t.GetStart()==oldpos:t.SetStart(newpos)
            if t.GetEnd()==oldpos:t.SetEnd(newpos)
for f in b.GetFootprints():
    if f.GetReference() not in ['C7','U3']:continue
    name={'C7':'C_KEMET_C315_P2.54_RoutedSilk','U3':'SOIC-8_3.9x4.9mm_P1.27mm_RoutedSilk'}[f.GetReference()]
    f.SetFPID(p.LIB_ID('Oscillator',name))
    lib=f.Duplicate();lib.SetOrientationDegrees(0);lib.SetPosition(p.VECTOR2I(0,0));lib.Reference().SetText('REF**')
    p.FootprintSave(str(root/'Oscillator.pretty'),lib)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones())
p.SaveBoard(str(path),b)
apply_metadata(path)
pro=json.loads((root/'oscillator.kicad_pro').read_text());rules=pro['board']['design_settings']['rules'];rules.update(min_hole_clearance=.30,min_hole_to_hole=.30,min_via_annular_width=.1,min_silk_text_height=.8,min_silk_text_thickness=.15)
for name in ['oscillator.kicad_pro','routing-candidate.kicad_pro']:(root/name).write_text(json.dumps(pro,indent=2))
dru='''(version 1)
(rule "General copper clearance" (constraint clearance (min 0.25mm)))
(rule "General track width" (constraint track_width (min 0.25mm)))
(rule "Board edge clearance" (constraint edge_clearance (min 0.5mm)))
(rule "Through via diameter" (condition "A.Type == 'Via'") (constraint via_diameter (min 0.6mm)))
(rule "Through via hole" (condition "A.Type == 'Via'") (constraint hole_size (min 0.3mm)))
(rule "PTH annular ring" (condition "A.Type == 'Pad'") (constraint annular_width (min 0.3mm)))
(rule "Via annular ring" (condition "A.Type == 'Via'") (constraint annular_width (min 0.1mm)))
(rule "Drill separation" (constraint hole_to_hole (min 0.3mm)))
'''
for name in ['oscillator.kicad_dru','routing-candidate.kicad_dru']:(root/name).write_text(dru)
re=p.LoadBoard(str(path));vias=[t for t in re.GetTracks() if isinstance(t,p.PCB_VIA)]
audit={'board_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'mask_expansion_mm':p.ToMM(re.GetDesignSettings().m_SolderMaskExpansion),'mask_min_web_mm':p.ToMM(re.GetDesignSettings().m_SolderMaskMinWidth),'all_vias_exposed':all(not v.IsTented(p.F_Cu) and not v.IsTented(p.B_Cu) for v in vias),'via_count':len(vias),'pth_annular_rings_mm':[]}
for f in re.GetFootprints():
    for pad in f.Pads():
        if pad.GetAttribute()==p.PAD_ATTRIB_PTH:
            size=pad.GetSize();hole=pad.GetDrillSize();ring=min(p.ToMM(size.x-hole.x),p.ToMM(size.y-hole.y))/2
            audit['pth_annular_rings_mm'].append({'ref':f.GetReference(),'pad':pad.GetNumber(),'min_annular_mm':ring})
(root/'fabrication-geometry-audit.json').write_text(json.dumps(audit,indent=2));print({k:v for k,v in audit.items() if k!='pth_annular_rings_mm'})
