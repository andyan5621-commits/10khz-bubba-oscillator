# Bounded layout-capacitance sensitivity

Date: 2026-10-22

This directory contains four derivative LTspice transients based on the completed
`reports/runtime-check/hardware_full.net` nominal hardware model. The copied
`hardware_full_reference.net` is unchanged. Each derivative adds only the
explicit shunt capacitor lines shown in its `.net` file. These capacitors are
screening assumptions, not values extracted from the PCB.

## Reproduction

Run with the Python environment that contains PyLTSpice, NumPy and SciPy:

```powershell
& 'C:\PythonSolvers\.venv\Scripts\python.exe' .\run_parasitic_sensitivity.py
```

The runner launches LTspice with `-Run -b`, a hidden window and an explicit
wait. Its working directory is this folder, which also contains local copies of
`OPA1656.LIB` and `1N4148_ON.lib`. It reads every saved waveform trace and uses
the same coherent 20-cycle analysis copied from the nominal validation. Use
`--summarize` to rebuild `summary.json` from already completed analyses without
rerunning LTspice.

## Accepted cases

| Case | Added assumption | Frequency change | Vpp change | SFDR change |
|---|---|---:|---:|---:|
| `par_ninv_5pf` | 5 pF, N_INV to GND | +0.0000485 Hz (+0.000000485%) | +0.0000607 V (+0.00131%) | -0.000622 dB |
| `par_limiter_1pf` | 1 pF each, LIM_P and LIM_N to GND | +0.186634 Hz (+0.001869%) | -0.001938 V (-0.04175%) | +0.018379 dB |
| `par_filter_5pf` | 5 pF each, F_J and F_IN to GND | -0.00000136 Hz | -0.023070 V (-0.49695%) | +0.006561 dB |
| `par_rc_nodes_5pf` | 5 pF each, RC1/RC2/RC3/VOUT to GND | -4.963607 Hz (-0.049714%) | -0.000269 V (-0.00580%) | -0.009331 dB |

All four accepted runs reached 50 ms, had completion logs, and passed the same
late-window settling check as the nominal validation.

## Numerical limitation

An earlier `par_limiter_5pf` attempt assumed 5 pF at each limiter threshold
node. LTspice found the operating point but did not complete 50 ms within the
300 s guard. Its partial waveform was rejected and no metric was taken from it.
This is a simulation runtime limitation, not evidence of circuit or hardware
instability. The later 1 pF limiter run completed and is the only accepted
limiter sensitivity result.

Binary `.raw` and `.op.raw` files are local run products and are excluded from
version control. The `.db` files are LTspice caches. JSON files are the
machine-readable accepted results.

## Scope limits

- No PCB capacitance, inductance, coupling, dielectric loss or return-path
  impedance was extracted.
- Added capacitors are lumped shunts to ideal ground; they do not model
  trace-to-trace coupling or electromagnetic field distribution.
- No component tolerances, temperature cases, cable variants or supply
  impedance sweeps were added.
- No topology or nominal component value was changed.
- These are model sensitivities, not hardware performance claims.

