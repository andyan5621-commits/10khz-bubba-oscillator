"""Workspace-only derivative simulations. Never edits recovered reference files."""
from pathlib import Path
import importlib.util
import json
import subprocess
import sys
import time
from PyLTSpice import RawRead

HERE = Path(__file__).resolve().parent
EXE = Path(r'C:\Users\20252928\AppData\Local\Programs\ADI\LTspice\LTspice.exe')
ANALYZER = HERE / 'oscillator_measurements.py'
spec = importlib.util.spec_from_file_location('archived_measurements', ANALYZER)
measure = importlib.util.module_from_spec(spec)
spec.loader.exec_module(measure)

def analyze(name):
    r = RawRead(HERE / f'{name}.raw', traces_to_read='*', verbose=False)
    axis = r.get_axis() + float(r.get_raw_property().get('Offset', 0))
    result = {'name':name, 'saved_end_s':float(axis[-1]), 'kind':'simulation, not hardware', 'method':'archived coherent 20-cycle interpolation; H2-H40; late-window settling comparison'}
    if axis[-1] < .04999:
        raise RuntimeError('Incomplete transient; refusing performance metrics')
    trace = 'V(adj_out)' if name == 'hardware_mid' else 'V(vfinal)'
    result['output_node'] = trace
    result['metrics'] = measure.analyze_waveform(axis, r.get_trace(trace).get_wave())
    if name == 'hardware_mid':
        import numpy as np
        result['steady_supply_currents_A'] = {}
        for rail in ('I(V1)','I(V2)'):
            mask = axis >= .04
            times = axis[mask]
            values = r.get_trace(rail).get_wave()[mask]
            result['steady_supply_currents_A'][rail] = {'mean_abs':float(np.trapezoid(np.abs(values), times)/(times[-1]-times[0])), 'peak_abs':float(np.max(np.abs(values)))}
    log = (HERE / f'{name}.log').read_text(errors='replace')
    if 'Total elapsed time:' not in log:
        raise RuntimeError('No completion record')
    (HERE / f'{name}-analysis.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({'name':name, **{k:result['metrics'][k] for k in ('freq','Vpp','SFDR','SFDR_all_bins','THD','settled')}}), flush=True)

def create_deck(name):
    text = (HERE / 'baseline.net').read_text(encoding='utf-8-sig')
    # Extra parts match confirmed hardware; bypass capacitors remain ideal models.
    additions = ['* Confirmed hardware additions; nominal component models only', 'XSPARE 0 spare Vcc Vss spare OPA1656']
    for n in range(1,5):
        additions.extend([f'CBP{n} Vcc 0 100n', f'CBN{n} Vss 0 100n'])
    additions += ['CBULKP Vcc 0 10u','CBULKN 0 Vss 10u']
    if name == 'hardware_mid':
        additions += ['RPOT_TOP Vfinal adj_out 5k','RPOT_BOTTOM adj_out 0 5k','RSCOPE adj_out 0 1Meg','CSCOPE adj_out 0 100p','.save V(adj_out) I(V1) I(V2)']
    else:
        additions += ['RPOT Vfinal 0 10k','RSCOPE Vfinal 0 1Meg','CSCOPE Vfinal 0 20p']
    if name == 'hardware_startup':
        text = '\n'.join(l for l in text.splitlines() if not l.upper().startswith('IKICK '))
        text = text.replace('.tran 0 50m 0 100n', '.tran 0 50m 0 100n startup')
        if 'startup' not in text:
            raise RuntimeError('Failed to set documented supply-ramp startup')
    text = text.replace('.end', '\n'.join(additions)+'\n.end')
    (HERE / f'{name}.net').write_text(text, encoding='utf-8')

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'baseline' or '--analyze-only' in sys.argv:
        analyze(mode)
    else:
        create_deck(mode)
        t = time.monotonic()
        proc = subprocess.run([str(EXE), '-Run', '-b', f'{mode}.net'], cwd=HERE, creationflags=subprocess.CREATE_NO_WINDOW, timeout=300)
        print(f'{mode}: exit={proc.returncode}, elapsed={time.monotonic()-t:.1f}s', flush=True)
        if proc.returncode:
            raise RuntimeError('Simulator returned failure')
        analyze(mode)
