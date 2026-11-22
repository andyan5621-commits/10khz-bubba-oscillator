# Reproducing the simulations

## Entry points

- `Measure_Oscillator_Final.py`: simulate the final drawn circuit once, or use
  `--raw path/to/file.raw` to analyze an existing completed waveform.
- `Buildable_sweep.py`: ordinary nested-loop search over realizable resistor
  combinations. `--dry-run` prepares the grid; `--check` runs one known point.
- `tolerance_final.py`: four-worker study of 256 independent ±1% timing-component
  combinations, followed by four separate RG/RF combinations.
- `oscillator_measurements.py`: shared coherent-waveform analysis.
- `Oscilator.py`: historical parameter-sweep/analysis tool, retained under its
  original filename. Its historical search ranges are distinct from the final
  discrete search; use the entry points above for the final-design workflow.

The scripts are retained from the project with repository-relative schematic
and generated-output paths. Measurement algorithms and design values were not
changed during repository packaging. They require Python, the packages in
`requirements.txt`, and an LTspice installation discoverable by PyLTSpice/spicelib.
The simulator launchers use Windows process flags and have not been ported to
Linux/Wine. The setup validation performed for this repository is documented in
`software-environment.txt`; it is not a fresh 256-corner simulation.

## Circuit variants

`simulation/ltspice/Oscillator_Final.asc` contains the final literal component
values and the original seven-channel signal path. Its output is Vfinal, before
the hardware-only potentiometer. The final measurement script runs an exact
schematic snapshot without adding an output load or other components.

`Oscillator.asc` is the starting schematic for the search. The discrete script
overrides resistor values and fixes C1–C4 at 10 nF, C5 at 1 nF and C6 at 68 nF.
It also adds the spare-channel follower, bypass capacitors, and 1 MΩ || 20 pF
output test load. This explains why the optimization and final-schematic runs
can have slightly different Vpp despite similar frequency and spectral results.

`optimized_best.net` is the saved winning netlist from run
`20260919-023613-263185`. Its circuit and local device models are retained; the
unused machine-specific standard.dio library reference was removed for portability.
The active diodes use the accompanying explicit D4148_ON model. Source-file
hashes are listed in `provenance.json`.

## Spectral interpretation

The analysis extracts the final part of the transient, locates complete cycles,
resamples a 20-cycle window, and checks successive windows for settling. The
harmonic result considers H2–H40; the all-bin result additionally considers other
resolved bins over the same approximate bandwidth. For the saved winner both
give 90.783 dB, with H3 dominant and bandwidth approximately 399.4 kHz.

These are deterministic model results, not calibrated noise measurements. The historical breadboard spectra use a 0–100 kHz span with Blackman–Harris windowing and averaging. The November PCB captures instead show a 0–90 kHz span at 180.18 kS/s with five RMS exponential averages. Simulation and the two hardware datasets are not identical analyses.

## Model provenance

- Texas Instruments OPA1656 model, Final 1.3, 25 August 2022.
- LTspice standard.dio 1N4148 entry marked mfg=OnSemi, retained as D4148_ON:
  Is=2.52 nA, Rs=0.568 Ω, N=1.752, Cjo=4 pF, M=0.4, tt=20 ns.
- OPA1656 datasheet and model resources: https://www.ti.com/product/OPA1656

Large `.raw` files, transient logs, and generated run directories are intentionally
ignored by Git. Keep archived results under `results/`; keep exploratory runs
under `runs/`.
