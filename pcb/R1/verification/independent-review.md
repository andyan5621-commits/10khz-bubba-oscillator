# Final independent review — R1-review-03

22 October 2026. Reviewed actual native files, independent netlist exports, completed simulation artifacts, the final fabrication package, and independent Gerber renders.

**Gate A electrical capture: PASS. Gate B footprint/placement review: PASS. Gate C routing review: PASS. Gate D engineering fabrication-package review: PASS. Overall prototype readiness: CONDITIONAL PASS.**

**No critical unresolved electrical or manufacturing issue was identified in this revision.** Ordinary incoming inspection, potentiometer insertion/retention and direction checks, controlled assembly/startup, and measured performance validation remain. These are not waived and are not claims of completed hardware validation. The package remains **UNRELEASED** until explicit user manufacturing/purchase approval. No upload, order, assembly or hardware measurement is authorized or performed by this review.

## Frozen reviewed artifacts

Package: `fabrication/review-packages/R1-review-03/`. Earlier packages are superseded: -01 failed preflight before production plots; -02 lacks the final visible R1 marking and finish/revision metadata.

| Artifact | SHA-256 |
|---|---|
| Native schematic | `cc4e9bd008f168a4e64262c612c48e86a04cea780c80a114a0fdfe0a20036169` |
| Native board | `a4f358f10eaf822501065362decd702d36b8ac9826cc2c7e55d44460478eb4e2` |
| Independent final netlist export | `2230e2a41b32b4042952db5aabe089032ad5f30d6429e3d21fe195f9d5f29d5b` |
| `R1-review-03-gerbers-UNRELEASED.zip` | `b7150ff62d955080c8e8bda7e1d0696d12e3df7a49b8af16baf8273b0053b478` |

Any CAD or production-export change invalidates the corresponding snapshot review until rechecked. Export timestamps can change a netlist hash without changing its connectivity.

## Independent electrical and routing checks

The original Desktop ASC and recovered LTspice decks were read directly. The independent checker does not import a CAD generator. It verifies all 32 OPA1656 package pins, seven active channels and a correctly terminated spare, ±15 V supplies, diode/bulk-capacitor polarity, supply/BNC/pot mapping, six signal capacitors, bypassing, eight authorized testpoints and the exact 44-resistor implementation across 15 series/parallel paths. The two R11 branches remain 2 kΩ and 100 kΩ in parallel; R12 remains 1 kΩ. A 10 kΩ pot spans VFINAL/GND with its wiper at OUTPUT.

The independently exported final schematic passes with **77 components, 44 fixed resistors and 51 nets**. The board has **81 footprints**: the same 77 electrical references plus only the four authorized H1–H4 mounting holes. All **172 electrical pad assignments** and footprint IDs match. H1–H4 are specifically checked at the approved coordinates, each one circular Ø2.7 mm NPTH with no electrical net. Their 3.05 mm hardware reservations clear neighboring pad copper; the nearest conservative pad-boundary distance is 5.26 mm.

I reran KiCad 9.0.6 on the actual unified -03 source package: **ERC zero violations; DRC zero violations, zero unconnected items and zero schematic-parity issues**. Bare testpoints remain on-board and are correctly excluded from purchased BOM flags. The full per-component inventory still lists all 77 references, with testpads marked NO_PURCHASE. Independent BOM reference/value/footprint checks pass; populated schematic MPNs agree. Resistor sourcing MPNs are recorded in the BOM rather than absent schematic MPN fields.

The routed board contains **591 track segments, 39 through vias and one filled bottom GND region**, plus four mechanical keepout zones. Actual front/back copper renders show a broadly continuous return plane; local bottom jumpers do not form a plane-wide split. Bypass pin-to-capacitor copper lengths are 3.71–4.93 mm for seven connections and 6.32 mm for U1's negative rail. The latter exceeds the aspirational 5 mm target slightly; the local bypass and direct plane return remain present.

The independent review found a redundant VOUT copper loop. Four segments totaling 7.407 mm were removed. Comparing the actual pre/post copper SVG primitives confirms exactly four removals and no additions. VOUT now totals 83.772 mm. The remaining R13 return detour avoids crossing the R4 chain/RC3 driven routes or introducing additional bottom transitions. The geometry review found mainly nearby bypassed-rail and short R4-chain parallels, not a long post-filter/output-aggressor run. Retaining the existing route and continuous plane is accepted as a documented tradeoff; no extracted coupling or hardware-SFDR guarantee is implied.

C7 and U3 use project-local routed-silk variants. Independent semantic comparisons confirm unchanged pads, holes, Fab bodies and courtyards; only silk width/segment changes differ. The final R1/ENIG metadata update leaves every footprint, track, via, filled zone and outline segment identical to the reviewed loop-cleaned board.

## Mechanical and process disposition

The board outline is **95 × 79 mm**, two copper layers, nominal 1.6 mm thickness and 35 µm copper, with ENIG explicitly recorded in the native stack and Gerber job. Visible top legend includes `10 kHz OSCILLATOR | R1`.

The exact Molex 39543-0003 hole pattern is accepted. Its centered body sketch remains approximate: clearance instead uses a conservative envelope containing the full possible 9.5 mm nominal depth on either side of the row plus margin. On the final enlarged outline that courtyard is at least 2.75 mm from the board edge. No guessed centering is represented as a verified manufacturer datum.

The Amphenol 031-5431-10RFX pattern and handedness are resolved from the actual manufacturer drawing. Small signal/shell holes, mounting-fork holes, mating direction and board-edge projection agree. Dedicated shell contact is GND; the two mechanical forks remain unnetted.

The approved Alps RK09K1130A5R uses the exact-model standard footprint. Contact/tab centers and nominal opening dimensions match Drawing 3. Its two 2.1×1.8 mm oval slots have 0.60 mm minimum annular rings; electrical-pin rings are 0.40 mm. These exceed the selected AISLER 0.30 mm PTH/slot rule; the 1.8 mm slot tool is supported. Missing tab-section/corner detail is ordinary fit uncertainty, not evidence of interference or a critical pre-fabrication sample requirement. Retain incoming insertion/retention checks. Current pin 1 VFINAL / pin 2 OUTPUT / pin 3 GND mapping is retained; record actual knob direction during assembly, with no unverified clockwise-increases claim.

All 39 vias explicitly have exposed mask openings. Native settings use 0.05 mm mask expansion and 0.10 mm minimum mask web. Reviewed silk meets the selected 0.15 mm stroke / 0.8 mm text constraints. Exact mechanical sources and reasoning are retained in `footprint-audit.md`, `gate-b-review.md` and `alps-slot-manufacturing-review.md`.

## Actual fabrication-export inspection

Independently verified **49 manifest entries**, source provenance and the **10-file ZIP** against the actual package bytes. No missing or changed file was found. The archive contains seven X2 plots, separate PTH/NPTH Excellon files and a Gerber job. Job metadata now says R1, ENIG, 1.6 mm and two layers.

The independent Gerbonara inspection in `fabrication/inspection/results/R1-review-03/` parses all layers without failures, finds one closed outline with centerline dimensions 95 × 79 mm, and reconciles drill counts with the native board. I additionally compared every Excellon feature's coordinates and diameter/slot endpoints directly against the native board: **85 round PTH drills, two plated routed slots and four NPTH drills match exactly**. The plated slot output uses a 1.8 mm cutter over 0.3 mm travel, reproducing the 2.1×1.8 mm footprint opening. The 39 Ø0.3 mm via drills are included in the round PTH count.

I viewed the actual -03 top, bottom and all-layer renderings. Drill-to-pad and mask-to-copper registration, hole/slot orientation, outline containment and visible revision marking agree; no shifted or mirrored data is apparent. These are fabrication-layer views, not assembled-board photographs. The job's 95.05×79.05 mm bounding size includes outline stroke width; the routed edge centerline remains 95×79 mm.

## Performance evidence and remaining conditions

Four completed 50 ms nominal LTspice cases were reviewed from actual decks/logs/waveform-analysis results: baseline 9984.3517 Hz / 4.952940 Vpp; full pot 4.642419 Vpp; no-kick supply-ramp startup 4.642419 Vpp; half pot into 1 MΩ ∥ 100 pF 2.316181 Vpp. Model SFDR is approximately 90.78–90.79 dB. Mean modeled rail current at half pot is approximately 37.32 mA each. All accepted cases settle in the analyzed late window.

Four completed added-capacitance screenings were also read directly: 5 pF at N_INV, 1 pF at each limiter threshold, 5 pF at both internal filter nodes, and 5 pF at all four timing nodes. The largest reported shifts are approximately −0.497% output amplitude for the filter case and −4.964 Hz frequency for the timing case. These assumptions are not extracted PCB capacitances and do not bound mutual coupling. A timed-out 5 pF limiter case has no accepted result.

The actual filter is unity-gain Sallen–Key with natural frequency about 10.16 kHz and Q about 4.12; 30 kHz is the third-harmonic region, not its pole frequency. The pot's approximately 6.27% nominal maximum-amplitude reduction is retained. The unbuffered output requires the documented high-impedance load, not a 50 Ω termination. Historical 46/256 timing-corner failures prevent an unconditional ±1% frequency claim.

Incoming inspection, ordinary pot fit/direction checks, the documented 60 mA-per-rail controlled startup, warm-up and matched prototype/PCB measurements remain required. No hardware amplitude, stability, frequency tolerance or SFDR result is claimed. The final package is ready for user review and supplier CAM review under the chosen process; manufacturing/purchase release remains the user's decision.

## Evidence index

- `final-electrical-results.json`, `current-electrical-results.json`: independent graph PASS.
- `routed-parity-results.json`, `package-erc-independent.json`, `package-drc-independent.json`: final package connectivity and native checks.
- `final-bom-results.json`, `silk-variant-independent-results.json`, `pad-geometry-stability-results.json`: inventory and pad geometry.
- `final-routed-length-results.json`, `front-copper-delta-results.json`, `final-revision-delta-results.json`: routing geometry and bounded changes.
- `final-j1-envelope-results.json`, `mounting-clearance-results.json`, `alps-slot-results.json`: mechanical checks.
- `package-integrity-results.json`, `drill-coordinate-parity-results.json`: exact final archive/drill reconciliation.
- `history/`: superseded initial/Gate B reviews; earlier rejection evidence remains available separately.
