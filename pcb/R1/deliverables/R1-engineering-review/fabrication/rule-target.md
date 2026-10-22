# Fabrication rule target — AISLER 2-layer ENIG

Proposed service: AISLER, two-layer 1.6 mm FR-4, 35 µm copper, ENIG, green mask, white legend. No upload, quote, release or purchase has occurred. Board revision and measured dimensions must be recorded after routing.

[Official rules](https://community.aisler.net/t/2-layer-1-6mm-35-m-enig-design-rules/3732), updated 7 July 2025, checked 22 October 2026:

| Feature | Supplier limit | Project target / verification |
|---|---|---|
| Track / space | 0.125 / 0.125 mm | 0.25 / 0.25 mm minimum |
| Copper to edge | 0.30 mm | 0.50 mm |
| NPTH to copper | 0.25 mm | ≥0.25 mm; mounting hardware envelope also clear |
| Drill spacing | 0.30 mm | ≥0.30 mm |
| PTH drill | 0.5–5.6 mm | Actual drill report |
| PTH annular ring | 0.30 mm | ≥0.30 mm, including slots |
| Via drill / ring | ≥0.25 / ≥0.10 mm | 0.30 / 0.15 mm or larger |
| PTH slot width | 0.7–2.6 mm | Alps slot width 1.8 mm; final fit/ring audit |
| Legend stroke / height | ≥0.15 / ≥0.80 mm | ≥0.15 / ≥0.80 mm |
| Legend to pad | ≥0.125 mm | DRC plus plotted-mask inspection |
| Mask dam / expansion | ≥0.10 / suggested 0.05 mm | Inspect SOIC and all drill lands |
| Tented vias | Unsupported | Exposed via openings |

The board must be checked against these values after all routing, zone fills and export settings are final. Datasheet package fits, electrical integrity and mounting clearances remain separate checks.
