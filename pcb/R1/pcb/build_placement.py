"""Generate the native KiCad 9 placement study. No routing or manufacturing plots.

Only import a schematic netlist when --netlist is explicitly supplied. The board
is a placement study until schematic approval and mechanical fit checks pass.
"""
from pathlib import Path
import argparse
import json
import hashlib
import csv
import xml.etree.ElementTree as ET
import pcbnew as p

ROOT = Path(__file__).resolve().parent
LIB = ROOT / "Oscillator.pretty"
SYSTEM = Path(r"C:\Program Files\KiCad\9.0\share\kicad\footprints")
LIB.mkdir(exist_ok=True)

def radial(name, pitch, width, depth, drill=0.85, pad=1.65):
    """Body centred about the two nominal lead positions; conservative courtyard."""
    x0=(pitch-width)/2; x1=x0+width; y=depth/2
    text=f'''(footprint "{name}" (version 20241229) (generator "pcbnew")
 (layer "F.Cu") (descr "Drawing-derived draft: physical fit check required")
 (attr through_hole)
 (fp_text reference "REF**" (at {pitch/2} {-y-1.4}) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))
 (fp_text value "{name}" (at {pitch/2} {y+1.5}) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))
 (fp_rect (start {x0} {-y}) (end {x1} {y}) (stroke (width 0.1) (type default)) (fill none) (layer "F.Fab"))
 (fp_line (start {x0-0.2} {-y-0.2}) (end {x1+0.2} {-y-0.2}) (stroke (width 0.12) (type default)) (layer "F.SilkS"))
 (fp_line (start {x0-0.2} {y+0.2}) (end {x1+0.2} {y+0.2}) (stroke (width 0.12) (type default)) (layer "F.SilkS"))
 (fp_rect (start {min(x0-0.6,-pad/2-0.25)} {-y-0.6}) (end {max(x1+0.6,pitch+pad/2+0.25)} {y+0.6}) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))
 (pad "1" thru_hole circle (at 0 0) (size {pad} {pad}) (drill {drill}) (layers "*.Cu" "*.Mask"))
 (pad "2" thru_hole circle (at {pitch} 0) (size {pad} {pad}) (drill {drill}) (layers "*.Cu" "*.Mask"))
)'''
    (LIB/f"{name}.kicad_mod").write_text(text,encoding="utf-8")

radial("C_Vishay_MKP1837310011_P5",5,7.5,5.5)
radial("C_Vishay_MKP1837368011_P5",5,7.5,7.5)
radial("C_AVX_SR215A102FARTR1_P5.08",5.08,5.08,3.18)
radial("C_KEMET_C315C104K5R5TA_P2.54",2.54,3.81,2.54,0.85,1.6)

def connector(name,body,courtyard,pads,description):
    x0,y0,x1,y1=body; cx0,cy0,cx1,cy1=courtyard
    lines=[f'(footprint "{name}" (version 20241229) (generator "pcbnew") (layer "F.Cu") (attr through_hole) (descr "{description}")',
      f'(fp_text reference "REF**" (at 0 {y1+1.5}) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
      f'(fp_text value "{name}" (at 0 {y1+3}) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))',
      f'(fp_rect (start {x0} {y0}) (end {x1} {y1}) (stroke (width 0.1) (type default)) (fill none) (layer "F.Fab"))',
      f'(fp_rect (start {cx0} {cy0}) (end {cx1} {cy1}) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))']
    for number,x,y,drill,size in pads:
        shape="rect" if number=="1" else "circle"
        lines.append(f'(pad "{number}" thru_hole {shape} (at {x} {y}) (size {size} {size}) (drill {drill}) (layers "*.Cu" "*.Mask"))')
    lines.append(")");(LIB/f"{name}.kicad_mod").write_text("\n".join(lines))

connector("J_Molex_39543-0003_Draft",(-2.5,-4.75,12.5,4.75),(-3.25,-10.0,13.25,10.0),[(str(i+1),5*i,0,1.2,2.2) for i in range(3)],"SD-39543-003 B2; verified 1.20 mm holes and 5.00 mm pitch; Fab body centred only for illustration; courtyard reserves full 9.5 mm depth on each side plus 0.5 mm margin")
# BNC datum: signal pin is origin, negative local y points toward mating face.
# MP1/MP2 are plated fork-post holes with no asserted electrical net.
connector("J_Amphenol_031-5431-10RFX_Draft",(-7.2,-33.65,7.2,1.15),(-7.7,-34.15,7.7,1.65),[("1",0,0,.89,1.75),("2",-2.54,0,.89,1.75),("MP1",-5.08,-5.08,2.01,3.3),("MP2",5.08,-5.08,2.01,3.3)],"31-5431-10RFX REV C; drawing-derived hole positions and top-view handedness independently reviewed; fork posts deliberately unnetted")

def mm(x): return p.FromMM(x)
def point(x,y): return p.VECTOR2I(mm(x),mm(y))
b=p.BOARD()
settings=b.GetDesignSettings()
settings.SetCopperLayerCount(2)
settings.SetBoardThickness(mm(1.6))
settings.m_MinClearance=mm(.25)
settings.m_TrackMinWidth=mm(.25)
settings.m_CopperEdgeClearance=mm(.5)
settings.m_HoleClearance=mm(.25)
settings.m_HoleToHoleMin=mm(.25)

def line(x1,y1,x2,y2,layer=p.Edge_Cuts,width=.05):
    s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_SEGMENT)
    s.SetStart(point(x1,y1));s.SetEnd(point(x2,y2));s.SetLayer(layer);s.SetWidth(mm(width));b.Add(s)

def text(msg,x,y,layer=p.Dwgs_User,size=1):
    t=p.PCB_TEXT(b);t.SetText(msg);t.SetPosition(point(x,y));t.SetTextSize(point(size,size));t.SetTextThickness(mm(.15));t.SetLayer(layer);b.Add(t)

# 95 x 70 mm candidate size, origin at 50,50 mm. Not an enclosure commitment.
for xy in [(50,50,145,50),(145,50,145,120),(145,120,50,120),(50,120,50,50)]: line(*xy)
text("PLACEMENT STUDY - NOT FOR FABRICATION",97.5,46,size=1.5)
text("95 x 70 mm candidate / 2 layers / 1.6 mm / 35 um Cu",97.5,124)
text("10 kHz oscillator  /  draft 2026-10-22",97.5,117,p.F_SilkS,1)
text("UNROUTED PLACEMENT STUDY",97.5,52.5,p.F_SilkS,1)

def envelope(name,x,y,w,h):
    for xy in [(x,y,x+w,y),(x+w,y,x+w,y+h),(x+w,y+h,x,y+h),(x,y+h,x,y)]:line(*xy,p.Dwgs_User,.15)
    text(name,x+w/2,y+h/2,size=.85)

# Exact Alps part selected by user; the pot is imported only when present in source.

positions={
 "U1":(69,72,0), "U2":(89,86,0), "U3":(108,90,0), "U4":(127,81,0),
 "C1":(79,63,0), "C2":(91,73,0), "C3":(85,98,0), "C4":(99,100,0),
 "C5":(111,101,0), "C6":(117,87,270),
 "C7":(74.8,68.7,0), "C8":(94.8,82.7,0), "C9":(108.5,84,0), "C10":(132.8,77.7,0),
 "C11":(61.5,79,90), "C12":(80.7,89.3,0), "C13":(99.7,91.3,0), "C14":(119,81.5,0),
 "C15":(73,108,0), "C16":(81,108,0),
}
capfps={**{f"C{i}":"Oscillator:C_Vishay_MKP1837310011_P5" for i in range(1,5)},
 "C5":"Oscillator:C_AVX_SR215A102FARTR1_P5.08", "C6":"Oscillator:C_Vishay_MKP1837368011_P5",
 **{f"C{i}":"Oscillator:C_KEMET_C315C104K5R5TA_P2.54" for i in range(7,15)},
 "C15":"Capacitor_THT:CP_Radial_D5.0mm_P2.00mm", "C16":"Capacitor_THT:CP_Radial_D5.0mm_P2.00mm"}

def footprint(ref, val, identifier, pos):
    library,name=identifier.split(":",1)
    path=LIB if library=="Oscillator" else SYSTEM/(library+".pretty")
    f=p.FootprintLoad(str(path),name)
    if not f: raise RuntimeError(f"Missing footprint {identifier}")
    f.SetReference(ref); f.SetValue(val); f.SetFPID(p.LIB_ID(library,name)); b.Add(f)
    x,y,deg=pos; f.SetPosition(point(x,y));f.SetOrientationDegrees(deg)
    f.Value().SetVisible(False)
    f.Reference().SetTextSize(point(.8,.8));f.Reference().SetTextThickness(mm(.12))
    return f

parser=argparse.ArgumentParser()
parser.add_argument("--netlist",type=Path)
args=parser.parse_args()
if args.netlist:
    source=ET.parse(args.netlist).getroot()
    fixed={"D1":(63.9,63,270),"D2":(64.2,73,180),"R13":(64.7,76.8,90),"R14":(69,68,0),"R15":(69,65,180),"R11":(127,88,0),"R16":(127,91,0),"R12":(127,95,90),"J1":(56,109,0),"J2":(132.05,99,270),"RV1":(123,60,0),"TP1":(75,114,0),"TP2":(81,114,0),"TP3":(87,114,0),"TP4":(70,87,0),"TP5":(101,85,0),"TP6":(109,94.2,0),"TP7":(122,104,0),"TP8":(127,99,0)}
    for base,count,x,y in [(101,4,78.5,58),(201,4,78,77.5),(301,4,76,92.5),(401,4,91,105.5),(501,3,56,65),(601,5,56,54),(701,3,56,83),(801,5,56,58),(901,3,102,81),(1001,3,110.5,102.5)]:
        for i in range(count): fixed[f"R{base+i}"]=(x+4.5*i,y,0)
    fixed.update({"R501":(65,60,180),"R502":(60.5,60,180),"R503":(56,60,180),"R601":(65,56.5,180),"R602":(60.5,56.5,180),"R603":(56,56.5,180),"R604":(55.5,63.5,0),"R605":(60,63.5,0),"R701":(60.5,69.5,0),"R702":(60.5,66.5,180),"R703":(56,68.5,270)})
    for i in range(5):fixed[f"R{801+i}"]=(55.5,76.5+4*i,270)
    for i in range(3):fixed[f"R{901+i}"]=(123.5,85.5+4.5*i,270)
    for i in range(3):fixed[f"R{1001+i}"]=(119.5-4.5*i,96.5,180)
    positions.update(fixed)
    fps={}
    excluded=set()
    manifest=[]
    for comp in source.findall("components/comp"):
        ref=comp.attrib["ref"]
        if ref in excluded: continue
        if ref=="RV1":ident="Potentiometer_THT:Potentiometer_Alps_RK09K_Single_Vertical"
        elif ref.startswith("TP"):ident="TestPoint:TestPoint_Pad_D1.5mm"
        elif ref.startswith("U"): ident="Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"
        elif ref.startswith("R"): ident="Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder"
        elif ref.startswith("D"): ident="Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal"
        elif ref=="J1": ident="Oscillator:J_Molex_39543-0003_Draft"
        elif ref=="J2": ident="Oscillator:J_Amphenol_031-5431-10RFX_Draft"
        else: ident=capfps[ref]
        fps[ref]=footprint(ref,comp.findtext("value"),ident,positions[ref])
        fps[ref].SetPath(p.KIID_PATH("/"+comp.findtext("tstamps").split()[0]))
        if ref in ["R301","R302","R303","R304","R701","R702","R703","R901","R902","R903","R204"]:
            x,y,_=positions[ref];fps[ref].Reference().SetPosition(point(x,y+1.7))
        if ref=="C1": fps[ref].Reference().SetPosition(point(81.5,67.4))
        if ref=="C3": fps[ref].Reference().SetPosition(point(85,103))
        if ref=="J2":
            fps[ref].Reference().SetPosition(point(132,110));fps[ref].Reference().SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T))
        if ref=="J1":fps[ref].Reference().SetPosition(point(61,97.5))
        if ref in ["R901","R902","R903"]:
            x,y,_=positions[ref];fps[ref].Reference().SetPosition(point(x-1.7,y));fps[ref].Reference().SetTextAngle(p.EDA_ANGLE(90,p.DEGREES_T))
        if ref=="R703":fps[ref].Reference().SetPosition(point(53.7,68.5));fps[ref].Reference().SetTextAngle(p.EDA_ANGLE(90,p.DEGREES_T))
        if ref=="R13":fps[ref].Reference().SetPosition(point(67,77));fps[ref].Reference().SetTextAngle(p.EDA_ANGLE(90,p.DEGREES_T))
        if ref=="U1":fps[ref].Reference().SetPosition(point(69,76.2))
        if ref=="R14":fps[ref].Reference().SetPosition(point(72,66.5));fps[ref].Reference().SetTextAngle(p.EDA_ANGLE(90,p.DEGREES_T))
        if ref=="R15":fps[ref].Reference().SetPosition(point(69,63.1));fps[ref].Reference().SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T))
        if ref=="R604":fps[ref].Reference().SetPosition(point(52.8,63.5));fps[ref].Reference().SetTextAngle(p.EDA_ANGLE(90,p.DEGREES_T))
        if ref=="R605":fps[ref].Reference().SetPosition(point(60,64.9))
        if ref=="C5":fps[ref].Reference().SetPosition(point(113.5,104.3))
        if ref=="C6":fps[ref].Reference().SetPosition(point(117,94.4));fps[ref].Reference().SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T))
        if ref=="TP6":fps[ref].Reference().SetPosition(point(106,94.2))
        if ref=="D2":
            for item in list(fps[ref].GraphicalItems()):
                if isinstance(item,p.PCB_TEXT) and item.GetText()=="K":fps[ref].Remove(item)
        status="DRAWING_DERIVED_FIT_PENDING" if ref.startswith("C") or ref.startswith("J") else "PROPOSED_PACKAGE_FIT_PENDING"
        if ref=="J2":status="DRAWING_PATTERN_AND_HANDEDNESS_VERIFIED_POSTS_UNNETTED"
        if ref=="J1":status="VERIFIED_HOLE_PITCH_FULL_POSSIBLE_DEPTH_COURTYARD_RESERVED"
        if ref=="RV1":status="USER_APPROVED_EXACT_MPN_MANUFACTURER_DRAWING_3_PATTERN_VERIFIED"
        if ref.startswith("TP"):status="APPROVED_1.5MM_PROBE_PAD"
        manifest.append({"reference":ref,"value":comp.findtext("value"),"footprint":ident,"status":status})
    with (ROOT/"footprint-manifest.csv").open("w",newline="") as fh:
        writer=csv.DictWriter(fh,fieldnames=["reference","value","footprint","status"]);writer.writeheader();writer.writerows(manifest)
    omissions=[]
    connections=[]
    for net in source.findall("nets/net"):
        n=p.NETINFO_ITEM(b,net.attrib["name"],int(net.attrib["code"]));b.Add(n)
        for node in net.findall("node"):
            ref,pin=node.attrib["ref"],node.attrib["pin"]
            if ref in excluded:
                omissions.append({"ref":ref,"pin":pin,"net":net.attrib["name"],"reason":"Mechanical footprint unresolved; no guessed pads"});continue
            matches=[pad for pad in fps[ref].Pads() if pad.GetNumber()==pin]
            if len(matches)!=1: raise RuntimeError(f"Expected one pad for {ref}.{pin}, found {len(matches)}")
            matches[0].SetNet(n)
            connections.append({"ref":ref,"pin":pin,"net":net.attrib["name"]})
    (ROOT/"placement-import-audit.json").write_text(json.dumps({"source_file":str(args.netlist),"source_sha256":hashlib.sha256(args.netlist.read_bytes()).hexdigest(),"schematic_component_count":len(source.findall("components/comp")),"placed_footprints":len(fps),"schematic_nets":len(source.findall("nets/net")),"mapped_pads":len(connections),"missing_footprints":sorted(excluded),"omitted_pins":omissions,"mapped_connections":connections,"status":"PARTIAL PLACEMENT - no routed connectivity or manufacturing approval"},indent=2))
    text(f"{len(fps)} footprints / 51 nets / no tracks / mechanical review pending",97.5,128)
    text("+15V   GND   -15V",61,95.8,p.F_SilkS,.8)
else:
    for ref,pos in positions.items():
        if ref.startswith("U"):
            footprint(ref,"OPA1656IDR","Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",pos)
        else: footprint(ref,"FIT REVIEW",capfps[ref],pos)
    text("No electrical nets yet. Schematic import gate open.",97.5,128)

p.SaveBoard(str(ROOT/"oscillator.kicad_pcb"),b)
if args.netlist:
    reloaded=p.LoadBoard(str(ROOT/"oscillator.kicad_pcb"))
    actual={(fp.GetReference(),pad.GetNumber()):pad.GetNetname() for fp in reloaded.GetFootprints() for pad in fp.Pads() if not pad.GetNumber().startswith("MP")}
    expected={(c["ref"],c["pin"]):c["net"] for c in connections}
    if actual!=expected: raise RuntimeError("Saved board pad mapping differs from imported source")
    audit=json.loads((ROOT/"placement-import-audit.json").read_text())
    audit.update(saved_board_pad_mapping_matches_source=True,saved_board_electrical_pad_count=len(actual),unnetted_mechanical_pads=["J2.MP1","J2.MP2","RV1.MP (2 plated slot pads)"])
    (ROOT/"placement-import-audit.json").write_text(json.dumps(audit,indent=2))
pro={"meta":{"filename":"oscillator.kicad_pro","version":1},
 "board":{"design_settings":{"rules":{"min_clearance":.25,"min_track_width":.25,"min_via_diameter":.6,"min_through_hole_diameter":.3,"min_copper_edge_clearance":.5,"min_hole_clearance":.25,"min_hole_to_hole":.25},"track_widths":[0,.25,.3,.5,.75],"via_dimensions":[{"diameter":.6,"drill":.3},{"diameter":.8,"drill":.4}]}},
 "net_settings":{"classes":[{"name":"Default","clearance":.25,"track_width":.3,"via_diameter":.6,"via_drill":.3,"microvia_diameter":.3,"microvia_drill":.1,"diff_pair_width":.3,"diff_pair_gap":.25,"diff_pair_via_gap":.25}],"meta":{"version":4},"netclass_assignments":{},"netclass_patterns":[]}}
(ROOT/"oscillator.kicad_pro").write_text(json.dumps(pro,indent=2))
(ROOT/"fp-lib-table").write_text('(fp_lib_table\n (version 7)\n (lib (name "Oscillator")(type "KiCad")(uri "${KIPRJMOD}/Oscillator.pretty")(options "")(descr "Part-specific draft footprints; fit review required"))\n)\n')
print(f"Saved {len(list(b.GetFootprints()))} footprints; {len(list(b.GetTracks()))} tracks; {b.GetNetCount()} nets.")
