# Independent fabrication export inspection

Candidate: `C:\Users\20252928\OneDrive - TU Eindhoven\Documents\ChatGPT\Oscillator PCB development\oscillator-pcb\fabrication\review-packages\R1-review-02`  
Inspected UTC: 2026-10-22T00:53:02.206045+00:00  
Parser: Gerbonara 1.6.3  
Automated result: **PASS (manual gates pending)**

This is an internal review result, not a manufacturing release or order approval.

## Package and geometry

- Manifest verified: `True`
- Generator classified by parser: `kicad`
- Board name: `oscillator-B`
- Board bounds: `{'min_x_mm': 49.975, 'min_y_mm': -126.025, 'max_x_mm': 145.025, 'max_y_mm': -46.975, 'width_mm': 95.05000000000001, 'height_mm': 79.05000000000001}`
- Outline centerline bounds: `{'min_x_mm': 50.0, 'min_y_mm': -126.0, 'max_x_mm': 145.0, 'max_y_mm': -47.0, 'width_mm': 95.0, 'height_mm': 79.0}`
- Closed outline polygons found: `1`

## Layer map

| Layer | File | X2 FileFunction | Bounds (mm) | Within outline range |
|---|---|---|---|---|
| bottom copper | `oscillator-B_Cu.gbl` | `('Copper', 'L2', 'Bot')` | `{'min_x_mm': 50.5005, 'min_y_mm': -125.4995, 'max_x_mm': 144.4995, 'max_y_mm': -47.5005, 'width_mm': 93.99900000000001, 'height_mm': 77.999}` | `True` |
| bottom mask | `oscillator-B_Mask.gbs` | `('Soldermask', 'Bot')` | `{'min_x_mm': 52.104316, 'min_y_mm': -123.895684, 'max_x_mm': 142.895684, 'max_y_mm': -49.104316, 'width_mm': 90.79136799999999, 'height_mm': 74.791368}` | `True` |
| bottom silk | `oscillator-B_Silkscreen.gbo` | `('Legend', 'Bot')` | `{'min_x_mm': 52.104316, 'min_y_mm': -123.895684, 'max_x_mm': 142.895684, 'max_y_mm': -49.104316, 'width_mm': 90.79136799999999, 'height_mm': 74.791368}` | `True` |
| mechanical outline | `oscillator-Edge_Cuts.gm1` | `('Profile', 'NP')` | `{'min_x_mm': 49.975, 'min_y_mm': -126.025, 'max_x_mm': 145.025, 'max_y_mm': -46.975, 'width_mm': 95.05000000000001, 'height_mm': 79.05000000000001}` | `True` |
| top copper | `oscillator-F_Cu.gtl` | `('Copper', 'L1', 'Top')` | `{'min_x_mm': 53.6, 'min_y_mm': -115.75, 'max_x_mm': 138.78, 'max_y_mm': -55.8, 'width_mm': 85.18, 'height_mm': 59.95}` | `True` |
| top mask | `oscillator-F_Mask.gts` | `('Soldermask', 'Top')` | `{'min_x_mm': 52.104316, 'min_y_mm': -123.895684, 'max_x_mm': 142.895684, 'max_y_mm': -49.104316, 'width_mm': 90.79136799999999, 'height_mm': 74.791368}` | `True` |
| top silk | `oscillator-F_Silkscreen.gto` | `('Legend', 'Top')` | `{'min_x_mm': 52.104316, 'min_y_mm': -124.363152, 'max_x_mm': 142.895684, 'max_y_mm': -49.104316, 'width_mm': 90.79136799999999, 'height_mm': 75.258836}` | `True` |

## Drills and routed slots

- PTH `oscillator-PTH.drl`: 85 drilled holes, 2 routed slots, bounds `{'min_x_mm': 55.4, 'min_y_mm': -114.15, 'max_x_mm': 138.135, 'max_y_mm': -57.2, 'width_mm': 82.73499999999999, 'height_mm': 56.95}`, within outline range `True`.
  - 0.300 mm tool: 39 drills, 0 slots; slot cut lengths mm: -
  - 0.800 mm tool: 8 drills, 0 slots; slot cut lengths mm: -
  - 0.850 mm tool: 28 drills, 0 slots; slot cut lengths mm: -
  - 0.890 mm tool: 2 drills, 0 slots; slot cut lengths mm: -
  - 1.000 mm tool: 3 drills, 0 slots; slot cut lengths mm: -
  - 1.200 mm tool: 3 drills, 0 slots; slot cut lengths mm: -
  - 1.800 mm tool: 0 drills, 2 slots; slot cut lengths mm: 0.300, 0.300
  - 2.010 mm tool: 2 drills, 0 slots; slot cut lengths mm: -
- NPTH `oscillator-NPTH.drl`: 4 drilled holes, 0 routed slots, bounds `{'min_x_mm': 52.15, 'min_y_mm': -123.85, 'max_x_mm': 142.85, 'max_y_mm': -49.15, 'width_mm': 90.69999999999999, 'height_mm': 74.69999999999999}`, within outline range `True`.
  - 2.700 mm tool: 4 drills, 0 slots; slot cut lengths mm: -

## Native-board cross-check

- Source SHA-256 `83c42e0e6dd5e9724a504b3fcdf5f9cd6286b4cc8741df543c93aea8980987d1`; 81 footprints (77 electrical + 4 NPTH mounts), 591 track segments, and 39 vias.
- Native drilled features: 46 round PTH pads, 2 PTH slots, 4 NPTH pads, plus 39 vias.
- Native drill sizes: `{'0.800x0.800': 8, '0.850x0.850': 28, '0.890x0.890': 2, '1.000x1.000': 3, '1.200x1.200': 3, '2.010x2.010': 2, '2.100x1.800': 2, '2.700x2.700': 4}`

## Automated findings

- No automated package-structure, parse, extent, or drill-separation failure was found.
- NOTE: Extent containment is a range check only; inspect the generated overlays for true registration and polarity.
- NOTE: Gerber positive/negative image semantics are parser-rendered; solder-mask openings must be checked visually.

## Manual release gates still required

- Open `top.svg`, `bottom.svg`, and `all-layers.svg` and visually verify drill-to-pad registration, mask-to-copper registration, outline closure, readable legend, and absence of mirrored or shifted data.
- Confirm every routed slot has the intended width, length, plating, and component association against the approved footprint drawings; automated counts do not establish mechanical fit.
- Compare the board dimensions and drill table with the routed native board and the selected supplier limits.
- Confirm the DRC/ERC reports and all gates in `fabrication/manufacturing-checklist.md` before release.
- Any source or export correction requires a new immutable review-package revision and a fresh inspection.
