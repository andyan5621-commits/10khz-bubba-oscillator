# R1 fabrication ordering guidance

**Engineering checks passed. User fabrication release and purchase approval are still required. Nothing has been uploaded or ordered.**

Use only `R1-review-03-gerbers-UNRELEASED.zip`, SHA-256 `b7150ff62d955080c8e8bda7e1d0696d12e3df7a49b8af16baf8273b0053b478`. The UNRELEASED label records the outstanding user gate; it does not mean the engineering checks failed. Do not send older review-01/02 files or the complete engineering-documentation ZIP as fabrication input.

## Proposed quote

Request an expedited bare-board quote from AISLER first. Its [published two-layer ENIG class](https://community.aisler.net/t/2-layer-1-6mm-35-m-enig-design-rules/3732) matches the selected nominal stackup, and it [advertises European bare-board manufacture in one business day](https://aisler.net/en-US). A live order-specific quote must establish actual acceptance, shipment and Netherlands arrival dates; the public claim is not a delivery commitment.

Quote three bare boards as a practical starting quantity for one assembly and spare boards, subject to the actual price and user approval. No assembly service or pick-and-place processing is required. Selected electronic parts are in the BOM; most through-hole parts and op amps are already reserved.

| Order parameter | Value |
|---|---|
| Revision | R1 |
| Board outline | 95.000 × 79.000 mm centerline; one rectangular board |
| Layers | 2 copper layers |
| Material / thickness | FR-4, nominal 1.6 mm |
| Copper | 35 µm / nominal 1 oz on both outer layers |
| Finish | ENIG |
| Mask / legend | Green mask, white top legend; no positive bottom legend artwork |
| Vias | Through vias, exposed; no tenting request |
| Drill data | Separate plated and non-plated Excellon, millimetres, absolute origin |
| Plated features | 85 round drills plus two routed pot slots; slot tool Ø1.8 mm with 0.30 mm centerline travel, 2.10 mm overall length |
| Non-plated features | Four Ø2.70 mm mounting holes |
| Panelization | None supplied; no user-defined panel |
| Assembly | Bare PCB only |

The Gerber job's 95.05 × 79.05 mm graphical bounds include the 0.05 mm outline stroke. The actual routed board edge is its centerline, 95 × 79 mm. Do not resize the artwork to force the stroked bounds to 95 × 79 mm.

After user fabrication approval, upload the exact archive for the selected supplier's analysis and inspect its preview for correct drill/slot recognition, layer order, outline and scale. Stop if the supplier changes geometry or flags ambiguous data; resolve and re-review any resulting source change. Record quantity, total price including VAT and shipping, fabrication service, courier, shipment date and estimated Netherlands arrival. Present that concrete quote for explicit purchase approval before payment.

An alternative European quote may be requested from Eurocircuits, with explicit acceptance of its quoted stackup/thickness. Overseas rapid-production services remain schedule contingencies; their advertised build time does not include international transit. The target 31 October assembly depends on actual receipt and time to inspect, solder and test. Earlier release improves margin; no arrival date is guaranteed.

## Receiving and assembly

Match the delivered board revision, outline and hole/slot pattern to the approved package. Perform the documented incoming checks and ordinary pot-retention check, then follow `assembly/assembly-and-test.md`. The design is not a qualified measurement source until actual hardware validation demonstrates the stated performance under documented loading and measurement conditions.
