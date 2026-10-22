from pathlib import Path
import json,hashlib
ns={};exec(Path('oscillator-pcb/verification/check_board_parity.py').read_text().split('netpath,boardpath=')[0],ns);p,c,o=ns['parse'],ns['children'],ns['one']
root=Path('oscillator-pcb/fabrication/review-packages');a=p((root/'R1-review-02/source/oscillator.kicad_pcb').read_text());b=p((root/'R1-review-03/source/oscillator.kicad_pcb').read_text())
result={k:c(a,k)==c(b,k) for k in ['footprint','segment','via','zone','gr_line']}
result['verdict']='PASS' if all(result.values()) else 'FAIL'
result['scope']='Exact semantic comparison of component geometry, copper, filled zones and outline between -02 and -03; revision text/stack metadata are outside this comparison'
print(json.dumps(result,indent=2));assert result['verdict']=='PASS'
