"""Export actual KiCad schematic and uncluttered 1:1 placement PDFs."""
from pathlib import Path
import hashlib, json, re, subprocess
ROOT = Path(__file__).resolve().parents[1]
CLI = Path(r'C:\Program Files\KiCad\9.0\bin\kicad-cli.exe')
drawings = ROOT/'assembly/drawings'
temporary = ROOT/'reports/pdf-review'
drawings.mkdir(exist_ok=True)
temporary.mkdir(exist_ok=True)
board = ROOT/'pcb/oscillator.kicad_pcb'
schematic = ROOT/'schematic/oscillator.kicad_sch'
s = board.read_text(encoding='utf-8')
spans = []
for match in re.finditer(r'\(fp_text user\s', s):
    depth = 0
    quoted = escaped = False
    for i in range(match.start(), len(s)):
        c = s[i]
        if quoted:
            if escaped: escaped = False
            elif c == '\\': escaped = True
            elif c == '"': quoted = False
        elif c == '"': quoted = True
        elif c == '(': depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                if '"F.Fab"' in s[match.start():i+1]: spans.append((match.start(),i+1))
                break
for a,b in reversed(spans): s = s[:a]+s[b:]
plot_board = temporary/'assembly-plot-only.kicad_pcb'
plot_board.write_text(s,encoding='utf-8')
commands = [
    ['sch','export','pdf','--output',drawings/'schematic-R1.pdf',schematic],
    ['pcb','export','pdf','--output',drawings/'placement-R1.pdf','--layers',
     'F.Fab,F.SilkS,Edge.Cuts','--mode-single','--black-and-white',
     '--exclude-value','--sketch-pads-on-fab-layers',plot_board],
]
for args in commands:
    subprocess.run([str(CLI),*map(str,args)],check=True)
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
(drawings/'provenance.json').write_text(json.dumps({
    'canonical_board_sha256':digest(board),'schematic_sha256':digest(schematic),
    'plotting_only_fab_reference_labels_removed':len(spans),
    'cad_geometry_modified':False,
    'pdfs':{p.name:digest(p) for p in drawings.glob('*.pdf')}
},indent=2),encoding='utf-8')
