# 10 kHz Bubba sine wave oscillator

A personal analog electronics project by **Andi An**, from analytical design and LTspice optimization to a working breadboard and an assembled R1 PCB.

**Final implementation documented 22 November 2026.** The R1 board has been manufactured, assembled and bench tested. Reported output is approximately **10.006 kHz**, adjustable from near zero to approximately **4.6 Vpp** into a high-impedance load, using external **±15 V** rails.

## Start here

- **[Final project report](docs/report/final-project-report.md)** — design, simulations, PCB engineering, assembly, measurements and limitations.
- [Hardware measurement record](pcb/R1/reports/hardware-measurement-log.md) and [machine-readable results](results/hardware/README.md).
- [Original PCB spectra and photographs](evidence/hardware/2026-11-20/README.md).
- [PCB source and manufacturing package](pcb/README.md).
- [Detailed soldering guide](pcb/R1/assembly/R1-detailed-soldering-guide.md) and [clear component map](pcb/R1/assembly/drawings/clear-map/R1-clear-component-map.pdf).

![Assembled oscillator PCB](evidence/hardware/2026-11-20/assembled-top.jpeg)

## Results and their scope

| Evaluation | Frequency | Output | Spectral evidence |
|---|---:|---:|---|
| Saved discrete LTspice winner | 9,984.352 Hz | 4.949660 Vpp | 90.783 dB modeled SFDR; variant without hardware pot loading |
| PCB pot-loaded simulation | approximately 9,984.35 Hz | 4.6424 Vpp | approximately 90.78 dB modeled SFDR |
| Breadboard at matching output | 10,052.85 Hz | approximately 4.40 Vpp | 91.08 dB recorded cursor separation |
| PCB three repeated captures | 10,006.08–10,006.29 Hz | calculated 4.40 Vpp | 89.70–90.67 dB selected-component cursor separation |

The PCB is closer to nominal frequency in this comparison. **Calibrated intrinsic SFDR ≥75 or ≥80 dBc has not been established.** The approximately 90 dB readings compare selected components; largest-spur selection and measurement-system residual remain unqualified. No spectral improvement over the breadboard is claimed. Timed drift and startup tests were not completed. Read the report before interpreting these figures as specifications.

## Circuit

Four buffered RC sections and a diode-limited gain stage form the Bubba oscillator. An isolation buffer feeds a resonant unity-gain Sallen–Key low-pass filter, followed by an output buffer, fixed divider and 10 kΩ linear output pot. Four OPA1656 duals provide seven signal-path channels and one grounded spare follower. The wiper output requires a high-impedance load; do not use a 50 Ω termination as an equivalent test condition.

The R1 board preserves the optimized component values. It is **95 × 79 mm**, two-layer FR-4, nominal 1.6 mm / 35 µm copper / ENIG. Archived ERC, DRC, unconnected and schematic-parity counts are zero. Independent design and fabrication review passed. These checks do not certify every physical solder joint or measured performance.

## Repository map

| Location | Contents |
|---|---|
| [Final report](docs/report/final-project-report.md) | Canonical end-project documentation |
| [Design notes](docs/design.md) | Effective values and development history |
| [Measurement overview](docs/measurements.md) | Breadboard and PCB evidence and limitations |
| [Simulation](docs/simulation.md) | Reproduction instructions, variants and models |
| [Results](results/README.md) | Saved simulation results and hardware CSV transcriptions |
| [Evidence](evidence/README.md) | Demonstration video, spectra and assembled-board photos |
| [PCB](pcb/README.md) | KiCad sources, BOM, released Gerbers, assembly and review |
| [Documentation index](docs/README.md) | Current documents versus historical records |
| [Change history](CHANGELOG.md) | Documentation milestones |

## Reproduce the simulations

The simulation tools were developed for Windows with LTspice installed. Linux/Wine simulation execution has not been validated. From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe simulation/scripts/Buildable_sweep.py --dry-run
.\.venv\Scripts\python.exe simulation/scripts/Measure_Oscillator_Final.py
.\.venv\Scripts\python.exe simulation/scripts/Buildable_sweep.py --check
```

Open `simulation/ltspice/Oscillator_Final.asc` for the final original schematic. See [simulation documentation](docs/simulation.md) before comparing circuit variants. Saved results were not rerun for this publication update. Historical timing corners include 46 of 256 frequency failures; no unconditional ±1% production tolerance is claimed.

## Build and use

Start with [the R1 overview](pcb/R1/README.md). Use the portable KiCad source and only the explicitly released manufacturing archive. Follow the assembly guide, current-limited power-up procedure and polarity checks before applying ±15 V. Keep the original reviewed snapshot intact when making a future revision, and rerun the relevant design checks after changes.

The [older Word report](docs/report/Oscillator_lab_report_performance_complete.docx) and dated procurement/review documents remain historical evidence, not the current project status or live supplier quotes. No open-source license has been selected. Third-party model notices remain in place; see [third-party notices](THIRD_PARTY_NOTICES.md).
