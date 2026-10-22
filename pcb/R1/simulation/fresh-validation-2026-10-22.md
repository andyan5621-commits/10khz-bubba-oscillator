# Fresh LTspice validation, 2026-10-22

## Verified execution

LTspice 26.0.2 ran the recovered generated netlist and three documented derivatives to 50 ms. Completed logs, local binary waveforms, exact decks and JSON analyses are under `../reports/runtime-check/`. The original source files were not altered. Binary waveforms are retained locally but excluded from Git due to size.

The initial schematic-only batch attempts produced no result; those were inconclusive. Running the recovered netlist with `-Run -b` and waiting for process completion succeeded. Each accepted result has a completion log and waveform endpoint at 50 ms. A waveform-reader configuration error in the first postprocessing attempt was corrected by requesting trace data explicitly; existing completed waveforms were then analyzed without rerunning or changing them.

| Case | Additions / startup | Frequency Hz | Output Vpp | Model SFDR dB | Model THD % | Late-window settled |
|---|---|---:|---:|---:|---:|---|
| Original baseline | Original kick pulse; no pot | 9984.3517 | 4.952940 | 90.78331 | 0.00289012 | Yes |
| Confirmed hardware nominal, full pot | 10 kΩ across divider; 1 MΩ || 20 pF measurement load; 8 local/2 bulk bypass capacitors; grounded spare follower; original kick | 9984.3517 | 4.642419 | 90.78334 | 0.00289011 | Yes |
| Confirmed hardware nominal, supply-ramp startup | Same additions; kick removed; LTspice `.tran ... startup` supply ramp | 9984.3517 | 4.642419 | 90.78322 | 0.00289016 | Yes |
| Confirmed hardware nominal, half pot | 5 kΩ + 5 kΩ pot segments; wiper loaded by 1 MΩ || 100 pF; same spare/bypass; original kick | 9984.3517 | 2.316181 | 90.79264 | 0.00288705 | Yes |

For full-scale cases output is VFINAL; this exact ideal endpoint needs no near-zero series approximation. For the half-pot case output is ADJ_OUT. The signal-path resistor values remain the original equivalent values; the CAD implementation expands them into the user's 44 physical resistors.

The half-pot case also saved source currents. Time-weighted mean absolute currents over 40–50 ms are 37.318 mA and 37.323 mA; sampled peaks are about 41.00 mA per rail. These nominal model figures support the proposed 60 mA per-rail initial bench limits but do not replace measured current or worst-case analysis.

## Measurement method and limits

The original archived analysis module is used read-only. It selects complete late cycles, interpolates a 20-cycle coherent record and compares consecutive windows for settling. Harmonic SFDR examines H2–H40; the all-bin SFDR also searches nonfundamental bins up to 40 times the fundamental (~399.4 kHz). Resolution is approximately 499.2 Hz. These model analyses do not have the same bandwidth, windowing, residual distortion or uncertainty as the archived 0–100 kHz bench analyzer, so their dB values are not interchangeable measurements.

The fresh baseline reproduces the archived nominal metrics. The pot load reduces the predicted maximum amplitude by about 6.27% including the added scope load. The historical breadboard result near 4.98 Vpp was acquired on physical components and equipment. This difference is recorded, not hidden or corrected by an unapproved resistor change. Approximately 5 Vpp remains a physical validation target, not a model guarantee.

## Assumptions

- Ideal ±15 V sources and ideal bypass capacitors; no regulator/source impedance model or measured ESR/ESL.
- Nominal OPA1656 macro-model and 1N4148 model from the recovered project.
- Nominal resistor/capacitor values and nominal 10 kΩ pot; no actual component measurements.
- Representative high-impedance 1 MΩ || 20 pF load, not a confirmed cable/instrument model.
- No PCB-extracted parasitics, contact noise, leakage, temperature sweeps or manufacturing variation.

## Open issues / actions not executed

- A single nominal supply-ramp startup does not certify all supply sequences, temperatures or component corners.
- Physical prototype/PCB amplitude and SFDR must be compared under identical load and acquisition settings.
- The archived 46/256 timing-corner failures still stand; no new tolerance sweep is claimed.
- One half-pot / 100 pF load case is checked. It does not establish arbitrary cable/load compatibility; layout-specific parasitics remain to be evaluated before final engineering approval.
- No hardware was assembled, powered or measured by these simulation runs.

## Actions completed

Four completed transients, completion/end-time checks, coherent waveform analysis, unchanged-baseline reproduction, confirmed-hardware nominal startup check and one intermediate-pot/capacitive-load case. No topology or optimized resistor-value changes.
