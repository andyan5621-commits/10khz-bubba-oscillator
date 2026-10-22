# R1 supplier recommendation and remaining purchases

Checked 22 October 2026 for delivery to the Netherlands. This is a public-price calculation and purchasing plan, not a supplier checkout quote or an order. No fabrication release or payment has been made. The engineering snapshot and its immutable ZIPs are unchanged.

## Recommended PCB service

Use **AISLER Beautiful Boards, 2-layer 1.6 mm ENIG, Blitz, three bare boards, UPS Express** for the reviewed R1 specification. Hand-assemble one board using the reserved parts; the other two boards are spares. Three is AISLER's minimum bare-board quantity, not three complete component sets.

The native outline is 95 × 79 mm, or 75.05 cm². AISLER publishes a €22 job fee plus €0.170/cm² per board for this service. Calculation: €22 + 75.05 × €0.170 × 3 = €60.2755 excluding VAT, approximately **€72.93 including 21% Netherlands VAT**. Standard untracked shipping is included. **UPS Express costs extra and is calculated at checkout from the delivery address/order; its amount is not yet verified.** Do not treat €72.93 as the delivered express total.

Sources: [official price formula](https://community.aisler.net/t/our-simple-pricing/102), [shipping charges and methods](https://community.aisler.net/t/shipping-methods/672), [reviewed ENIG fabrication rules](https://community.aisler.net/t/2-layer-1-6mm-35-m-enig-design-rules/3732).

## Delivery estimate and deadline

The [current service-status table](https://community.aisler.net/t/service-status/399) lists **five working days** for 2-layer ENIG Blitz and **one to two working days for EU UPS Express** (current figure: two). This supersedes the generic one-day manufacture headline quoted in earlier project notes. Saturdays and Sundays are excluded, and the supplier states a 06:00 CET submission cutoff; the actual acceptance/dispatch date shown by the order controls.

| First accepted production day | Calculated dispatch | Planning estimate for receipt with 1–2 working day UPS Express |
|---|---|---|
| Thursday 22 October | Wednesday 28 October | Thursday 29–Friday 30 October |
| Friday 23 October | Thursday 29 October | Friday 30 October–Monday 2 November |
| Monday 26 October | Friday 30 October | Monday 2–Tuesday 3 November |

These dates are calculations from published working-day lead times, not carrier commitments. The broader shipping guide allows 1–5 business days for EU UPS Express, so delays beyond the table remain possible. Free post is estimated at 4–14 working days within the EU and is unsuitable for the 31 October target. Ordering on the originally planned 24–25 October weekend is unlikely to leave time for receipt, assembly and validation by 31 October with ENIG.

For comparison, ENIG Budget is approximately €40.95 including VAT for three boards, but takes ten manufacturing working days before transit. It does not suit this deadline.

A schedule contingency is AISLER **HASL Blitz**, approximately €61.76 including VAT for three boards plus express shipping, with two manufacturing working days. If production begins 23 October, the corresponding typical receipt calculation is 27–28 October. This changes the reviewed surface finish: it is **not the released R1 ENIG specification**. Before selecting it, check HASL-specific mask dams/pad clearances, update finish metadata and reissue manufacturing approval. Do not silently order the ENIG package as HASL. [HASL rules](https://community.aisler.net/t/2-layer-1-6-mm-35-m-hasl-design-rules/3735).

## Parts still to purchase for one populated PCB

### Required electronics

- **One Alps RK09K1130A5R**, 10 kΩ linear PCB potentiometer, already approved by the user. [DigiKey NL listing](https://www.digikey.nl/en/products/detail/alps-alpine/RK09K1130A5R/21721633): €1.46 excluding VAT / approximately **€1.77 including VAT**, before shipping. The English listing reports stock, while indexed regional pages differ; confirm checkout stock rather than relying on the cached count.
- **44 fitted 0805 thin-film resistors**, 0.1% tolerance, 25 ppm/°C. Buy **74 total** to include two spares of each of the 15 values. The existing breadboard's axial resistors are not the fitted package for this PCB. Order cut tape, not full reels or a paid custom reel.

| Value | Fit | Buy with spares | Exact manufacturer part number |
|---|---:|---:|---|
| 47 Ω | 4 | 6 | YAGEO RT0805BRD0747RL |
| 100 Ω | 2 | 4 | YAGEO RT0805BRD07100RL |
| 200 Ω | 2 | 4 | YAGEO RT0805BRD07200RL |
| 220 Ω | 2 | 4 | YAGEO RT0805BRD07220RL |
| 270 Ω | 4 | 6 | YAGEO RT0805BRD07270RL |
| 330 Ω | 4 | 6 | YAGEO RT0805BRD07330RL |
| 680 Ω | 2 | 4 | YAGEO RT0805BRD07680RL |
| 1 kΩ | 8 | 10 | YAGEO RT0805BRD071KL |
| 2 kΩ | 1 | 3 | YAGEO RT0805BRD072KL |
| 4.7 kΩ | 2 | 4 | YAGEO RT0805BRD074K7L |
| 10 kΩ | 3 | 5 | YAGEO RT0805BRD0710KL |
| 20 kΩ | 4 | 6 | YAGEO RT0805BRD0720KL |
| 47 kΩ | 1 | 3 | Vishay TNPW080547K0BEEA |
| 100 kΩ | 3 | 5 | YAGEO RT0805BRD07100KL |
| 300 kΩ | 2 | 4 | YAGEO RT0805BRD07300KL |

The exact BOM quantities are in [draft_bom.csv](../bom/draft_bom.csv); its Reserved_qty and Planned_order_qty columns keep existing stock separate. The older REVIEW/Required_release_data fields describe initial engineering gates; the final independent report records their disposition.

Allow roughly **€10–15 for the resistor lot** as a planning allowance, not a verified 15-line cart total. For scale, [DigiKey's 47 Ω listing](https://www.digikey.nl/nl/products/detail/yageo/RT0805BRD0747RL/5139357) shows €0.1089 including VAT at quantity one; other values and the Vishay part need their own current prices. No substitution is authorized by this allowance.

DigiKey's Netherlands listing states **€25 delivery below €75**, free delivery above that threshold, with typical delivery within three days depending on location. Confirm how shipping VAT is presented in the actual cart. Consolidate the pot and resistors into one order where stock permits; avoid paying separate shipping for the €1.77 pot. Ordering the exact parts through an existing combined order may save more than changing the design.

### Mechanical items and equipment, only if not already available

- Four M2.5 standoffs and matching screws/nuts for the four Ø2.7 mm board holes. Keep screw-head/washer diameter at or below 6 mm and use enough underside clearance for through-hole leads; 10 mm standoffs are a practical bench choice. Final fastener lengths depend on the chosen standoff/base.
- Optional knob compatible with the Alps 6 mm shaft. A knob is not electrically required; match the exact shaft profile rather than diameter alone.
- Three insulated supply wires for +15 V, GND and −15 V and suitable connections to the existing supply. Reuse the prototype's current-limited dual supply if available. A new supply is only needed for standalone use without that equipment.
- BNC measurement cable if not already owned. Use a high-impedance measurement input as documented; do not add a 50 Ω terminator as a routine accessory.
- Solder, flux, tweezers, fine-tip soldering iron, desoldering braid, magnification and compatible flux-cleaning materials if not already available. No stencil is needed for the intended hand-solder assembly.
- Optional enclosure/base. No enclosure has been selected or mechanically qualified; do not buy one based solely on the partial 3D preview.

The four op amps, 16 fitted capacitors, two diodes, terminal block and BNC jack are already reserved according to the user's inventory. No SOIC-to-DIP adapters, breadboard headers or jumper kit are needed on this PCB. The eight test points are copper probe pads and do not require separate purchased parts.

## Next purchasing action

Obtain the actual ENIG Blitz + UPS Express checkout quote and dispatch/arrival estimate for the delivery address. If that misses the deadline, decide explicitly whether to pursue the HASL contingency. User fabrication release and explicit approval of actual costs are still required before ordering. No supplier design upload, paid transaction or supplier message was performed by this update.
