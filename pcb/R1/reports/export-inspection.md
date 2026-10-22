# Independent fabrication export inspection

Status: **PASS — R1-review-03 export content is internally consistent; user release/order approval remains required**

Inspected 22 October 2026 with workspace-local Gerbonara 1.6.3 and KiCad
9.0.6's bundled `pcbnew`. Candidate:
`fabrication/review-packages/R1-review-03`.

No fabrication data was uploaded, quoted, released, ordered, or purchased.

## Immutable package and native-board evidence

- All 49 entries in the package `SHA256.json` manifest were present and matched.
- The packaged native board SHA-256 is
  `a4f358f10eaf822501065362decd702d36b8ac9826cc2c7e55d44460478eb4e2`,
  matching `source-provenance.json` and the supplied final-candidate hash.
- Native inspection found 81 footprints (77 electrical and four NPTH mounting
  footprints), 591 track segments, 39 vias, and 180 pads.
- The packaged DRC report contains zero violations, zero unconnected pads, and
  zero footprint errors. The packaged ERC report contains zero messages,
  errors, and warnings.
- The Gerber job declares KiCad/Pcbnew 9.0.6, revision R1, two copper layers,
  1.6 mm board thickness, and ENIG finish.

## Plot set, dimensions, and registration

The independent parser classified exactly these seven X2 plots, with no
unrecognized or extra fabrication layer:

| Role | File | X2 FileFunction |
|---|---|---|
| Top copper | `oscillator-F_Cu.gtl` | `Copper,L1,Top` |
| Bottom copper | `oscillator-B_Cu.gbl` | `Copper,L2,Bot` |
| Top mask | `oscillator-F_Mask.gts` | `Soldermask,Top` |
| Bottom mask | `oscillator-B_Mask.gbs` | `Soldermask,Bot` |
| Top legend | `oscillator-F_Silkscreen.gto` | `Legend,Top` |
| Bottom legend | `oscillator-B_Silkscreen.gbo` | `Legend,Bot` |
| Profile | `oscillator-Edge_Cuts.gm1` | `Profile,NP` |

The `.gbrjob` file lists the same seven plot files. The outline is one closed
rectangular contour with 95.000 × 79.000 mm centerline dimensions. Its plotted
95.050 × 79.050 mm extent is the expected result of the 0.05 mm outline stroke.
All copper, mask, legend, PTH, and NPTH extents lie within the plotted profile.

The color-separated top, bottom, and combined independent renders were visually
inspected. The drill centers and routed slots align with their copper lands and
mask openings; the mask openings align with copper; the four mounting holes are
at the four corners; and no layer is visibly mirrored, shifted, or outside the
profile. The top legend is readable, is clipped away from pad openings, and
visibly includes `10 kHz OSCILLATOR | R1`. The bottom plot has no intentional
positive legend artwork. Exposed via openings are visible, consistent with the
selected service's no-tented-via constraint.

Review renders and the machine-readable evidence are in
`fabrication/inspection/results/R1-review-03/`:

- `top.svg` / `top.png`
- `bottom.svg` / `bottom.png`
- `all-layers.svg` / `all-layers.png`
- `inspection.json` / `inspection.md`

## Drill and slot reconciliation

The files are separate, absolute-coordinate, metric Excellon outputs. Their X2
declarations are `Plated,1,2,PTH` and `NonPlated,1,2,NPTH`.

| Tool / feature | Export count | Native-board reconciliation |
|---|---:|---|
| 0.30 mm PTH via drills | 39 | 39 native vias |
| 0.80 mm PTH drills | 8 | 8 pads |
| 0.85 mm PTH drills | 28 | 28 pads |
| 0.89 mm PTH drills | 2 | 2 BNC signal pads |
| 1.00 mm PTH drills | 3 | 3 pads |
| 1.20 mm PTH drills | 3 | 3 terminal-block pads |
| 2.01 mm PTH drills | 2 | 2 BNC shield pads |
| 1.80 mm routed PTH slots | 2 | 2 native 2.10 × 1.80 mm oblong holes |
| 2.70 mm NPTH drills | 4 | 4 mounting-hole pads |

The PTH file therefore contains 85 circular drills plus two routed slots. The
slot route uses a 1.80 mm tool over a 0.30 mm centerline path, producing the
native 2.10 × 1.80 mm finished geometry. The NPTH file contains four circular
drills and no slots. Every count matches the packaged native board.

## Revision comparison and parser notes

After removing only creation timestamps and the changed revision attribute,
R1-review-02 and R1-review-03 have identical top/bottom copper, top/bottom mask,
bottom legend, outline, PTH, and NPTH command streams. The top legend changed as
intended to add R1. This supports the stated scope: legend and manufacturing
metadata changed; copper, pads, outline, mask, and drills did not.

Gerbonara emitted a syntax warning because KiCad places `G90` immediately after
the Excellon header terminator. Both drill files explicitly declare absolute,
metric, decimal coordinates, parsed completely, matched native counts and
extents, and rendered in registration. The warning is an ordering-style warning,
not evidence of an ambiguous unit, origin, scale, or missing drill operation.

## Remaining release boundary

This inspection establishes package integrity, plot/drill structure, native
count agreement, dimensions, and visible registration. It does not establish
component fit from physical samples, enclosure fit, supplier acceptance, live
lead time, or purchase approval. Any board/export change requires a new immutable
revision and a fresh inspection. Manufacturer upload and ordering must wait for
the remaining project gates and explicit user approval.
