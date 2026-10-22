# Fabrication and components — final R1 status

22 October 2026. **Engineering package PASS; user release and purchase approval pending.**

## Verified facts

All reserved electronic parts have exact MPNs. The exact Alps RK09K1130A5R was explicitly approved. The 44-element resistor implementation preserves the requested series/parallel values; selected 0805 thin-film parts are 0.1%, 25 ppm/°C. The procurement plan includes 74 resistor pieces (two spares per value) and one pot, separate from the user's reserved components. Stock must be rechecked when ordering.

The final board is 95 × 79 mm, two layers, nominal 1.6 mm FR-4, two 35 µm copper layers, ENIG, green mask and white legend. AISLER's actual published rule class is recorded in fabrication/rule-target.md. Native ERC/DRC/schematic parity and independent manufacturing inspection passed. Final Gerber/drill archive is R1-review-03 only; -01/-02 are superseded.

Seven X2 layers, 85 circular plated holes, two routed 1.8 mm pot slots with 0.3 mm centerline travel, and four Ø2.7 NPTH mounts were checked against native dimensions and coordinates. Exact component footprints were reviewed; BNC handedness and conservative Molex clearance are resolved. The Alps standard footprint is accepted without a blanket sample prerequisite; ordinary insertion/retention and direction checks remain.

## Assumptions and implementation choices

Bare-board manufacture followed by hand assembly. No enclosure geometry has been specified; the board has four M2.5 support holes and an outward-projecting BNC mating section. Native 3D previews omit some purchased part bodies, so enclosure fit cannot be inferred from them. Two silk-only footprint variants preserve all electrical pad geometry.

## Open actions

User fabrication release, live dated quote (quantity, total cost, shipping, Netherlands arrival estimate), explicit purchase approval, then procurement, receiving inspection, assembly and measured validation. AISLER European expedited manufacture is the first quoting candidate; Eurocircuits is an alternative subject to its quoted stackup. An October 31 receipt/assembly date is not guaranteed.

## Completed

Exact BOM/reference join; manufacturer/datasheet and footprint review; sourcing assessment; fabrication rule selection; native/manufacturing output generation; independent coordinate/visual inspection; assembly, first-power and SFDR/THD procedures. Detailed evidence: reports/export-inspection.md and verification/independent-review.md.

## Not executed

No supplier upload, live quote, financial transaction, order, physical assembly, power-up or new-PCB hardware measurement. Simulation and historical breadboard results are separately identified in the final engineering summary.
