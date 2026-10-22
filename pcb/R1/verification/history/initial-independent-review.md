# Independent verification — release gate

Review date: 22 October 2026, updated after the 02:09 CEST correction. Scope: actual recovered source and generated native artifacts, independently of the chief's summary.

**Current readiness verdict: FAIL. Do not fabricate or power this revision.**

**Electrical source-capture verdict: PASS for the corrected native schematic.** This limited pass does not clear the footprint, board, performance, or fabrication gates. I independently ran KiCad's netlist export on the corrected native file; the resulting graph passes all implemented electrical checks, with 69 components, 44 fixed resistors and 51 nets. `current-electrical-results.json` records the full result. The independently exported netlist SHA-256 is `919a3d347e77074febdaf3157b2d89865e3f64fcca54f80a7c13a97c0ba5f48d`. Native schematic SHA-256 is `c28186a0f055473b29cc4519acad8294f56c211d3c71f88665c14b47c69158af`. Changes invalidate this snapshot approval until rechecked.

The inspected board contains 20 footprints, zero tracks, zero vias, zero zones, and only the empty net definition. Its SHA-256 is `95636e4ce2b699056c9323bb41493cc7cf611f0c085417a88ae122ba412314ef`. It is a placement skeleton, not an electrically implemented board. The empty `placement-drc.json` violation list cannot establish electrical completeness on a board with no assigned nets. See `placement-audit.json`.

## Observed evidence

Read the original Desktop `Oscillator works/Oscillator_Final.asc`, its archived LTspice-generated netlist, and `C:/Users/20252928/Documents/Codex/projects/10khz-bubba-oscillator/simulation/ltspice/optimized_best.net` directly. The original drawn source has seven active channels, ±15 V, and the exact Sallen–Key topology described below. The optimized net additionally contains an artificial scope load, spare channel, and bypassing; those are not all original drawn components. The user-confirmed 10 kΩ pot and physical resistor networks are separate requirements.

The first legacy `oscillator.net` export contained no components or nets, despite a successful file creation. It cannot substantiate connectivity.

The first populated native export was independently examined and preserved as `rejected-initial-native-export.net`, with the matching schematic `rejected-initial-native.kicad_sch`. It has 53 physical components, 28 fixed resistors and 35 nets. Export SHA-256: `37327a2b60a54b77a3fcaa39cb03fcfd5bb0d37bc62ea01e06dc0f5dba6c9af9`.

## Critical failures in the rejected initial export — corrected in the current capture

1. All four OPA1656 packages connect pin 4 (V−) to +15 V and pin 8 (V+) to −15 V. This is destructive reverse supply polarity, not a cosmetic symbol issue.
2. Every amplifier's inverting/non-inverting inputs are exchanged. Followers feed output to the positive input; the oscillator gain stage grounds its negative input. The captured circuit is not the source circuit.
3. Both electrolytics have reversed polarity: C15 positive at ground/negative at +15 V; C16 positive at −15 V/negative at ground.
4. Supply-connector outer pins and BNC signal/shell pins are opposite the stated intended mapping. Pot outer pins also reverse the planned rotation sense.
5. Only 28 fixed resistors exist. Six functional resistors R5–R10 are not expanded into the user's series networks. Correct nominal equivalents alone do not satisfy the explicit physical implementation.

The failures were sent immediately to the chief and schematic engineer. The common cause was consistent with a vertical coordinate inversion during legacy-symbol conversion. All listed electrical failures are resolved in the independently re-exported corrected graph. Its ERC report also has zero errors and zero warnings; that is corroborating evidence, not the basis for the pin-map pass.

## Independent verification method

`check_export.py` parses the actual KiCad exported netlist, without importing the schematic generator. It checks all 32 physical amplifier pins, diode polarity, polarized bulk capacitors, supply/output/pot pin mapping, signal capacitors, bypass count/values, and 44 fixed resistors across 15 independent paths. Each series-chain intermediate node must have exactly two resistor pins and no additional load. Parallel R11 branches must independently connect the same endpoints. The expected physical component total is 69: 44 fixed resistors, 16 capacitors, four dual op amps, two diodes, two connectors, one pot.

The expected graph was transcribed from the original LTspice-generated source and the confirmed physical networks, not inferred from the generator. The archived first failure results are in `rejected-initial-results.json`.

A passing script means only that this electrical capture matches the reviewed expectations. It cannot certify footprint geometry, routing, stability, performance, assembly, or fabrication readiness. A new source hash/export is required after changes.

## Analytical cross-checks

The filter is a unity-gain Sallen–Key low-pass: 1.9 kΩ then 1.9 kΩ feed the follower positive input; C5=1 nF shunts that input to ground; C6=68 nF connects the resistor junction to the follower output. Its ideal transfer denominator is `1 + s*C5*(R9+R10) + s²*R9*R10*C5*C6`. Thus its natural frequency is about 10.16 kHz and Q is about 4.12. It is resonant near the fundamental; 30 kHz is the third-harmonic region, not its pole frequency. This result is derived directly from the two nodal equations and does not assume the chief's topology label.

The 2 kΩ || 100 kΩ upper divider equals 1960.784 Ω. With the confirmed 10 kΩ pot across the retained 1 kΩ lower resistor, ideal full-scale gain is about 0.31677 rather than the 0.33775 of the unloaded fixed divider. The wiper has no following buffer. At approximately half rotation its source impedance is on the order of 2.66 kΩ (assuming an ideal output buffer); a 50 Ω instrument termination is unsuitable for reproducing high-impedance measurements. The BNC connector's nominal 50 Ω construction does not create a requirement for a 50 Ω load.

The unloaded nominal timing RC frequency is about 9.66 kHz. RG loads the last stage, so this calculation cannot establish the exact oscillator frequency or ±1% tolerance compliance.

## Manufacturer cross-checks

[TI OPA165x datasheet, Rev C](https://www.ti.com/lit/ds/symlink/opa1656.pdf): OPA1656IDR is dual SOIC-8; pins 1/7 are outputs, 2/6 inverting, 3/5 non-inverting, 4 V−, and 8 V+. ±15 V lies within the recommended supply range. All eight channels, including the terminated spare, draw quiescent current; the typical 3.9 mA/channel implies approximately 31.2 mA rail current before signal-load effects. This is an estimate, not a power-up current-limit authorization.

The exact [user-supplied Molex drawing](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/395/39543/395430002_sd.pdf?inline=) currently returns SD-39543-003 revision B2. It includes 39543-0003, 15 mm body length, 5 mm pitch and Ø1.20 mm PCB holes. The draft BOM's stated 1.40 mm manufacturer hole pattern is therefore not supported by that drawing. A deliberately enlarged hole needs a separate engineering rationale. Do not substitute the superficially similar 39543-3003 drawing. Orientation and exact body envelope must be verified visually before acceptance.

The [Amphenol 031-5431-10RFX part page](https://www.amphenolrf.com/en-us/part/031-5431-10rfx/1887/) links [this current customer drawing](https://www.amphenolrf.com/en-us/assets/file/4065791754/). Exact pad geometry and board-edge datum still require visual drawing review; no generic BNC land pattern is accepted by this audit.

## Other unclosed release gates

- No successful fresh LTspice waveform/log is available. Exit code zero without output is not simulation evidence. The confirmed pot and actual intended load must be represented before output performance claims.
- Only a placement skeleton exists in the inspected board. Footprint pin correspondence, no-connects, shorts, open nets, decoupler proximity, ground return continuity, board-edge clearances, courtyards and mounting remain unverified.
- Resistor manufacturer parts, stress/tolerance/tempco and the unbranded selected pot's pin geometry are unresolved. Reserved-part identity does not verify physical fit.
- A valid DRC and netlist equivalence check on the final board, full physical-reference BOM and 1:1 fit checks are required.
- Historical breadboard and archived simulation results cannot establish new-PCB SFDR. The cited archived timing corners already show that nominal success is insufficient for unconditional ±1% frequency compliance.

Critical blockers cannot be waived by calling this a conditional pass. No fabrication outputs or orders are authorized by this review.

