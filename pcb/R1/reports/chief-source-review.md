# Chief source review — preliminary

## Verified facts

- Read original source candidate `C:/Users/20252928/OneDrive - TU Eindhoven/Desktop/Oscillator works/Oscillator_Final.asc` directly.
- Read archived `simulation/ltspice/optimized_best.net`, `docs/design.md`, `docs/measurements.md`, and provenance in `C:/Users/20252928/Documents/Codex/projects/10khz-bubba-oscillator`.
- Inspected the archived potentiometer/decoupling drawing and near-full-output spectrum image directly.
- Circuit source uses seven OPA1656 channels, external +15/-15 V, four 1647 Ω / 10 nF sections, RG 10 kΩ, RF 48 kΩ, symmetric 130 kΩ/325 kΩ limiter networks, 1900 Ω filter resistors, 1 nF/68 nF capacitors, 1960.78431 Ω/1000 Ω output divider.
- Actual filter connectivity is a unity-gain Sallen–Key stage: two series resistors feed the follower noninverting input, one capacitor shunts that input to ground, and one feeds the resistor junction from the follower output. Initial user context called this MFB; preserve recovered connections instead of changing topology to fit that label.
- Archive explicitly documents a 10 kΩ pot across the divider output and ground, with wiper output. R11 and R12 remain installed. This is a later hardware addition absent from the final ASC.
- Source screenshot visibly displays fundamental 10052.83 Hz, cursor separation 88.79 dB, Vpk 2.49 V, SINAD 72.84 dB. This is historical acquisition evidence, not a new measurement or independently calibrated SFDR certification.

## Assumptions / pending reconciliation

Archive describes the intended working prototype, subject to user confirmation that no later changes supersede it. Archived image labels alone do not prove current physical wiring.

## Proposed modifications

None to optimized oscillator or filter values. PCB package mapping, physical resistor networks and unused eighth-amplifier termination require documented implementation decisions.

## Open issues

- Remaining stock geometry and chosen potentiometer.
- Exact current prototype match, including any later troubleshooting changes.
- Output loading is material: 10 kΩ in parallel with the retained 1 kΩ divider lower leg reduces nominal full-scale divider gain from approximately 0.33775 to 0.31677 (about 6.2%). This is already part of the archived hardware arrangement; do not silently compensate by changing resistor values.
- Output is unbuffered after the potentiometer. A 50 Ω BNC termination is not equivalent to the archived high-impedance measurements.

## Actions completed

Source inspection, metadata inventory, image inspection; specialist parallel work launched; version-controlled workspace initialized; actual KiCad CLI version 9.0.6 confirmed.

## Not executed

No new physical measurement, no approved schematic, no completed PCB, no DRC, no manufacturing export, no release or purchase.
