# Oscillator PCB — R1 engineering review

**Engineering checks passed; awaiting your final fabrication approval. No order has been placed.**

[Complete R1 engineering delivery ZIP](deliverables/Oscillator-PCB-R1-Engineering-Review.zip) · [Delivery integrity result](deliverables/delivery-integrity.json). The archive contains 117 hash-verified files; it is documentation plus source, not the ZIP to upload to a PCB manufacturer.

The native KiCad design preserves the recovered working oscillator and confirmed prototype values. It uses the approved Alps RK09K1130A5R potentiometer, exact reserved through-hole parts, 44 physical resistor elements and eight bare probe pads.

- [Final engineering summary](reports/final-engineering-summary.md)
- [Independent verification](verification/independent-review.md)
- [Fabrication export inspection](reports/export-inspection.md)
- [Open the portable KiCad project](fabrication/review-packages/R1-review-03/source/oscillator.kicad_pro)
- [Gerber/drill review ZIP](fabrication/review-packages/R1-review-03/R1-review-03-gerbers-UNRELEASED.zip)
- [Per-component BOM](bom/per-component.csv), [grouped BOM](bom/grouped-bom.csv), [procurement quantities](bom/draft_bom.csv)
- [Assembly and test instructions](assembly/assembly-and-test.md)
- [Printable schematic](assembly/drawings/schematic-R1.pdf), [placement drawing](assembly/drawings/placement-R1.pdf)
- [Task board](reports/task-board.md), [decisions](reports/decision-log.md), [risks](reports/risk-register.md)

The board is 95 × 79 mm, two layers, nominal 1.6 mm FR-4 / 35 µm copper / ENIG. Final ERC, DRC, unconnected and native schematic-parity counts are all zero. Independent engineering package review passed; ordinary incoming fit and physical performance validation remain required. Earlier review-01/02 directories are superseded and are not manufacturing inputs.

The `source` folder in the final candidate keeps the project, schematic, board, rules and custom libraries together for KiCad 9. Working directories remain under schematic/ and pcb/; the candidate is an immutable reviewed snapshot. Do not edit the snapshot and then reuse its checks or hashes.

No new PCB has been physically tested. Simulated SFDR is not measured hardware performance. The intended October 31 assembly date depends on the live manufacturing/shipping quote and parts receipt; it is not guaranteed. Both final fabrication release and any purchase require explicit user approval.
