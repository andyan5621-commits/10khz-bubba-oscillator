# Printable KiCad drawings

- `schematic-R1.pdf`: complete native schematic, A3 sheet. Net labels on left-hand pins are justified away from symbols for readability.
- `placement-R1.pdf`: component-side assembly view, nominal 1:1 on A4 landscape. Print at **actual size / 100%**, with all automatic fit-to-page scaling disabled. Check that the board outline measures **95 × 79 mm** on the physical print before using it for a fit check.

The placement drawing combines actual footprint body outlines, pads and board silkscreen. Duplicate fabrication-layer reference text was removed only from a disposable plotting copy to keep the drawing readable; the canonical PCB was not changed. Track routing is omitted for assembly clarity. The BNC envelope projects outside the board. The Molex centered body sketch is approximate: actual collision clearance uses the larger conservative courtyard documented in the independent review.

These PDFs are assembly/reference drawings. Only the separately reviewed Gerber/drill archive is manufacturing input. Neither a preview nor a paper fit check proves electrical performance.
