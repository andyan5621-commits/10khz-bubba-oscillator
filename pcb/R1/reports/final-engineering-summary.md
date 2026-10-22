# R1 engineering summary

22 October 2026. **ENGINEERING REVIEW PASSED; awaiting user fabrication release. No user fabrication release, upload or purchase has occurred.**

## Verified facts

The working oscillator was reconstructed from the recovered final LTspice source and reconciled with the user's physical resistor networks, bypass parts and confirmed output potentiometer. The original topology and effective resistor/capacitor values are preserved. The post-filter is a unity-gain Sallen–Key circuit; the initial description as a 30 kHz multiple-feedback filter was not consistent with the actual source. No redesign was made to match that initial description.

The native KiCad 9 project contains 77 schematic components/probe pads and 81 board footprints including four board-only mounting holes. It retains 44 physical fixed resistors, four dual OPA1656 packages, 16 capacitors, two diodes, the exact reserved terminal/BNC, the user-approved Alps RK09K1130A5R, and eight bare PCB test pads. The unused eighth amplifier is a grounded follower. The supply is external ±15 V; the final 10 kΩ pot remains across the retained divider with its wiper feeding the BNC.

The two-layer board is 95 × 79 mm, nominal 1.6 mm FR-4 with 35 µm outer copper and ENIG. It has 591 track segments, 39 exposed through vias, a continuous bottom ground plane and four 2.7 mm NPTH mounting holes for M2.5 hardware. The R1 revision is marked on silkscreen. The layout uses the manufacturer's supported fabrication limits, with 0.25 mm minimum track/space and 0.5 mm copper-to-edge clearance.

The final unified project passed ERC with zero violations and native DRC with zero violations, zero unconnected items and zero schematic-parity issues. Independent graph checking verifies all 44 resistor elements, all 32 amplifier pins, diode/electrolytic polarity, power and signal connections. Independent review removed a redundant copper loop from the VOUT timing net before final export. The remaining timing return route is accepted as a documented placement/return-path tradeoff, not claimed to be the shortest mathematically possible route.

Final manufacturing inspection independently verified all seven intended Gerber layers, 85 circular plated drills, two routed potentiometer slots and four non-plated mounting holes against the actual native geometry. All 49 candidate manifest entries and all 10 fabrication ZIP entries match. Gate D engineering package review: PASS; overall prototype readiness: CONDITIONAL PASS pending normal incoming checks, hardware measurements and user release.

Final board SHA-256: `a4f358f10eaf822501065362decd702d36b8ac9826cc2c7e55d44460478eb4e2`. The immutable candidate is `fabrication/review-packages/R1-review-03`; its source provenance and file manifest identify the exact schematic, board, project rules, BOM, PDFs and manufacturing exports. Earlier review-01/02 directories are superseded and must not be ordered.

## Simulation evidence and limits

Fresh nominal LTspice results reproduce the archived baseline. With the confirmed 10 kΩ pot and representative 1 MΩ ∥ 20 pF load, the model settles at approximately 9,984.35 Hz and 4.6424 Vpp, with approximately 90.78 dB modeled SFDR. A no-kick supply-ramp startup and a half-pot case into 1 MΩ ∥ 100 pF also settle. These are simulation results, not measurements of the new PCB.

Four bounded capacitance sensitivity runs settled. Assumed 5 pF on each timing node shifted frequency by about −4.96 Hz; 5 pF on each internal filter node changed amplitude by about −0.497%. A symmetric 1 pF limiter case and 5 pF inverting-input case had smaller effects. The attempted 5 pF limiter case timed out and has no accepted result. No PCB capacitance was extracted, no trace-to-trace coupling model was established and no hardware performance improvement is guaranteed.

Archived breadboard evidence shows 10,052.83 Hz, approximately 4.98 Vpp and an 88.79 dB fundamental-to-H3 cursor separation. It does not establish calibrated full-band intrinsic SFDR. The PCB must meet the user's ≥75 dBc threshold with a valid documented measurement method; ≥80 dBc remains the objective. The model's lower full-scale amplitude is recorded rather than compensated by changing optimized resistor values. Archived timing-corner frequency failures also remain part of the risk record.

## Accepted implementation choices

- Exact Alps part selected with explicit user approval; no unverified TinyTronics substitute.
- 0805 thin-film resistors selected at 0.1%, 25 ppm/°C while retaining every requested series/parallel element.
- Eight small probe pads only on supply, ground and buffered/output nodes.
- Two local footprint variants shorten silkscreen to clear exposed vias; pad geometry is unchanged and independently checked.
- The Molex body courtyard conservatively reserves the full possible depth about its verified hole row. Its centered Fab illustration is not a verified offset dimension.
- The exact-model standard Alps footprint is accepted; ordinary insertion/retention and knob-direction checks remain part of assembly.

## Assembly, sourcing and schedule

The BOM identifies all fitted parts and separates reserved stock from planned purchases. The remaining electronics purchase list is the selected pot plus 74 resistors, including two spares of each of 15 values. Mounting hardware and an optional 6 mm-shaft knob are separate mechanical choices. No order has been placed; distributor stock must be rechecked at checkout.

The assembly package contains a physical-reference resistor build sheet, all component coordinates, a test-point map, printable schematic/placement drawings, current-limited first-power instructions (±15 V, initially 60 mA per rail), repeated startup tests, warm-up/drift records, amplitude checks and matched prototype/PCB SFDR/THD procedures. No board has been fabricated, assembled, powered or physically tested by this work.

AISLER's European expedited bare-board service is the first quoting candidate for the selected stackup; Eurocircuits is an alternative subject to accepting its quoted thickness/service. Manufacture and shipping dates require a live quote. The October 24–25 release target falls on a weekend and October 31 is Saturday; delivery and assembly by October 31 are not guaranteed. An earlier approved order would improve the available margin.

Native 2D and 3D previews come from the actual CAD. Some through-hole capacitor, connector and pot body models are absent from the 3D preview; it is not a complete enclosure-clearance model. Their footprint geometry is checked separately against drawings and the 2D assembly view.

## Open actions

The final independent package review passed with no known unresolved critical electrical or manufacturing issue. Ordinary incoming component-fit checks and bench validation remain conditions of prototype use. Obtain the user's final fabrication approval, obtain and approve a dated quote, purchase boards/components, then assemble and execute the documented hardware tests. No unresolved critical electrical/manufacturing issue may be waived for schedule.
