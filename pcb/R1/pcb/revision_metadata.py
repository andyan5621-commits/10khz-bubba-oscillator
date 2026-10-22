"""Apply declared R1 fabrication metadata; no copper or pad geometry changes."""
import re
import pcbnew as p

STACKUP='''
		(stackup
			(layer "F.SilkS" (type "Top Silk Screen"))
			(layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))
			(layer "F.Cu" (type "copper") (thickness 0.035))
			(layer "dielectric 1" (type "core") (thickness 1.51) (material "FR4"))
			(layer "B.Cu" (type "copper") (thickness 0.035))
			(layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))
			(layer "B.SilkS" (type "Bottom Silk Screen"))
			(copper_finish "ENIG")
			(dielectric_constraints no)
		)
'''

def apply_metadata(path):
    text=path.read_text()
    if '(stackup' not in text:text=text.replace('\t(setup\n','\t(setup\n'+STACKUP,1)
    else:text=re.sub(r'\(copper_finish "[^"]*"\)','(copper_finish "ENIG")',text)
    path.write_text(text)
    board=p.LoadBoard(str(path));title=board.GetTitleBlock();title.SetRevision('R1');board.SetTitleBlock(title)
    p.SaveBoard(str(path),board)
