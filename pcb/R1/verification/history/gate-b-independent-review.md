# Independent review — current routing gate

Review date: 22 October 2026, 02:31 CEST. This report replaces the initial review; rejected artifacts and earlier results remain under `history/` and the explicitly named rejected/accepted-69part files.

**Gate A electrical capture: PASS. Gate B placement and footprint readiness for routing: PASS. Overall manufacturing readiness / Gate D: FAIL — incomplete, not released.**

Routing may proceed on the reviewed placement. This pass does not approve fabrication, assembly, energizing hardware, or measured performance. The actual board still has zero tracks, zero vias and zero copper zones, with 121 unconnected items. Those are expected for this gate and remain real blockers to fabrication.

## Reviewed artifacts and reproducible evidence

The native schematic has 77 components, 44 fixed resistors and 51 nets. All components have assigned footprints: 44 R, 16 C, 4 dual OPA1656 packages, 2 diodes, 2 connectors, the approved Alps RK09K1130A5R and 8 testpoints. Native schematic SHA-256: `f11b03281e3de57234baf2bfe2de979b84454128af9a501dfd3290187f08301a`.

An independent KiCad CLI export, `independent-77part-export.net`, passes the independently written graph checker. Export SHA-256: `db4309e90db8f39b5bcc9b7374eec0ae2105f04ac0c81896c65c51fab455c881`. `current-electrical-results.json` and `current-77part-results.json` contain the current PASS. Timestamp differences can change the export hash without changing the graph; the native source hash identifies the actual schematic reviewed.

The actual native board contains 77 footprints and 172 electrical pads. `board-parity-results.json` records exact pad-net and assigned-footprint equivalence, with no missing references or electrical pads. Board SHA-256 at this placement gate: `fc563e3fd8f07d75a60595b487e37900a8af61dcbb88f0dad0806679e87f3773`. Mechanical mounting pads are unnetted. This comparison establishes pad assignment, not routed connectivity.

I separately ran KiCad 9.0.6 DRC on that board. `placement-drc-independent.json` records zero geometric violations and 121 unconnected items. The DRC result does not erase the unrouted connections. Routing or other board edits require later parity/DRC review against the resulting revision.

## Electrical source preservation

The original Desktop `Oscillator works/Oscillator_Final.asc`, recovered generated netlist and archived optimized deck were read directly. The original signal circuit is distinguished from simulation instrumentation, later bypasses, spare-channel termination, and user-authorized pot/testpoints.

The checker does not import either CAD generator. It checks all 32 amplifier package pins; seven active channels and a grounded, closed-loop spare; ±15 V rail polarity; diode and bulk-capacitor polarity; supply/output connectors; the retained output divider and 10 kΩ pot; all signal capacitors and bypasses. It independently collapses resistor-only intermediate nodes and verifies the exact 44 elements across 15 physical series/parallel paths. Intermediate nodes must have no additional loads. The two parallel R11 paths remain 2 kΩ and 100 kΩ, with the 1 kΩ R12 retained.

Testpoints match the authorized mapping: TP1 +15 V, TP2 GND, TP3 −15 V, TP4 GAIN_OUT, TP5 N_BUF, TP6 VFILTERED, TP7 VFINAL, TP8 OUTPUT. They do not introduce probes on timing/filter summing or limiter junctions.

The filter is a unity-gain Sallen–Key low-pass. Direct nodal analysis gives denominator `1 + s*C5*(R9+R10) + s²*R9*R10*C5*C6`; its natural frequency is approximately 10.16 kHz and Q approximately 4.12. The previous 30 kHz cutoff description was incorrect: that is the third-harmonic region. No topology or value was altered to hide that discrepancy.

## Mechanical findings relevant to routing

The detailed current evidence is in `gate-b-review.md` and `footprint-audit.md`.

- **J1 Molex 39543-0003:** three Ø1.20 mm holes at 5 mm pitch are verified against the exact drawing. The centered Fab body sketch remains illustrative because its row-to-body datum has not been independently established visually. A conservative courtyard instead contains the full possible 9.5 mm nominal depth on either side of the row, with another 0.5 mm, and 0.75 mm extra at each width endpoint. Actual board courtyard bounds are x52.75–69.25, y99–119 mm, inside the rectangular board x50–145, y50–120 mm. Minimum edge clearance is 1.0 mm; no neighboring courtyard collision is reported by independent DRC. `j1-envelope-results.json` records the calculation. This supports routing without claiming a guessed center as fact.
- **J2 Amphenol 031-5431-10RFX:** the original manufacturer drawing confirms 10.16 mm mounting-post span, 5.08 mm row separation, Ø0.89 mm contacts and Ø2.01 mm mounting holes. With mating direction negative Y, the actual pattern has signal at (0,0), shell at (−2.54,0), and mounting forks at (±5.08,−5.08). Rear-elevation geometry resolves handedness. Mounting forks remain unnetted; the dedicated shell contact is GND.
- **RV1 Alps RK09K1130A5R:** exact-model standard footprint contact pitch, pin numbering, tab centers and body envelope agree with Drawing 3. Pin 2 is the wiper. The nominal 2.1×1.8 mm oval plated slots have the drawing's overall dimensions; the drawing does not specify corner radii or the tab section, so final drill/retention fit must not be represented as an independently proven exact slot-shape match. Standard-footprint use is accepted on its explicit exact-model support, matched dimensions and centers, and process compatibility. No interference is demonstrated. The ordinary incoming insertion/retention check is not a critical pre-fabrication blocker; final drill outputs must reproduce the accepted footprint.

RV1 currently maps pin 1 to VFINAL, pin 2 to OUTPUT and pin 3 to GND. The reviewed manufacturer drawing shows the shaft at full CCW but does not explicitly map that position to an electrical endpoint; the official FAQ diagrams do not resolve it either. The chief has confirmed retaining this mapping, with an assembly direction check and no clockwise-increases silkscreen claim. This is an unresolved usability detail, not an electrical or fabrication safety failure.

## Fresh simulation evidence

Completed LTspice decks, logs, binary waveform artifacts and analysis JSON now exist for four 50 ms runs under `reports/runtime-check/`. I read the actual decks/logs/analysis results; the earlier batch attempt with no resulting artifacts is superseded. These are simulations, not measurements.

| Case | Frequency | Output | Model SFDR |
|---|---:|---:|---:|
| Original baseline | 9984.3517 Hz | 4.952940 Vpp | 90.78331 dB |
| Confirmed circuit, full pot, 1 MΩ ∥ 20 pF | 9984.3517 Hz | 4.642419 Vpp | 90.78334 dB |
| Same circuit, no kick, supply-ramp startup | 9984.3517 Hz | 4.642419 Vpp | 90.78322 dB |
| Half pot, 1 MΩ ∥ 100 pF at wiper | 9984.3517 Hz | 2.316181 Vpp | 90.79264 dB |

The half-pot value is ADJ_OUT, not VFINAL. Its modeled mean absolute rail currents are approximately 37.32 mA each, with approximately 41 mA sampled peaks. All cases reach the 50 ms endpoint and the analysis reports late-window settling. The fresh baseline reproduces the archived nominal result.

The 10 kΩ pot loads the retained divider and reduces predicted maximum output by approximately 6.27%; values were not silently adjusted to recover 5 Vpp. The wiper is unbuffered and intended for a high-impedance instrument load. A 50 Ω BNC construction does not imply that a 50 Ω termination is appropriate.

These nominal macro-model runs omit PCB parasitics, real rail impedance, contact effects and component variation. One supply ramp and one mid-position capacitive load do not certify all conditions. The archived 46/256 timing-corner failures remain relevant to ±1% frequency compliance. Hardware SFDR requires matched load, bandwidth and acquisition settings; no new hardware measurement is claimed.

## Remaining manufacturing-release requirements

Complete routing and filled returns, then independently verify copper connectivity, schematic parity, final DRC and analog placement/return paths. Review final drill and slot outputs, body/board-edge access and verify that exported pot slots reproduce the accepted pattern; retain the ordinary incoming retention-fit check. Reconcile the full physical-reference BOM, assembly polarity/numbering and stock identities with final CAD. Inspect the actual exported fabrication package and document physical startup and matched performance checks. These remaining gates cannot be waived by the current routing pass.

Proposed AISLER ENIG process follow-up: `alps-slot-manufacturing-review.md` and `alps-slot-results.json` establish PASS for RV1 annular rings and slot-tool dimensions. The mechanical tab fit uncertainty is specifically bounded there; it is not a blanket physical-sample requirement.

