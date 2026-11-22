> **Hardware results:** [November PCB and breadboard CSV data](hardware/README.md). The simulation records below are retained separately and are not hardware measurements.

# Recorded simulation results

These files preserve previously completed project runs, not new simulations
performed while creating the repository. Some JSON/JSONL records contain original
Windows file paths for historical provenance; those paths are not portable links.

## Discrete optimization

Source run: `20260919-023613-263185`.

- `best.json`: winning component values, resistor recipes, and measured metrics.
- `summary.txt`: readable result and physical resistor combinations.
- `sweep_plan.json`: planned candidate grid.
- `measurements.jsonl`: per-candidate completed measurements.
- Runnable winner: `../simulation/ltspice/optimized_best.net`.

Nominal winner: 9,984.352 Hz, 4.949660 Vpp, 90.783 dB harmonic and all-bin SFDR.

## Tolerance study

Source run: `tolerance_final_20260919-214143-291681`.

- `nominal.csv`: separate nominal reference, 4.95294 Vpp.
- `RC_sweep.csv`: all 256 combinations of the eight timing components at ±1%.
- `rgfr_sweep.csv`: four independent RG/RF corner cases.

All 256 timing simulations returned valid records; 46 frequencies are outside
9.9–10.1 kHz. Timing-corner frequency range: 9,791.91–10,182.58 Hz. The recorded
corner SFDR is harmonic-based; an all-bin value was not separately tabulated for
each corner. The sweeps are sensitivity/corner checks, not yield predictions.
