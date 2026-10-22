# Fabrication and component readiness report

Report date: 22 October 2026  
Release target: 24–25 October 2026  
Desired Netherlands delivery/assembly: assemble by 31 October 2026  
Status: **GATES A/B PASSED; ROUTING AND FINAL MANUFACTURING REVIEW IN PROGRESS; NO PURCHASE OR RELEASE**

Current integration note: the exact Alps part is user-approved. The 77-part schematic passes ERC and independent graph comparison; the corresponding 172 board-pad connections and footprint identities pass independent comparison. Drawing-based routing readiness is accepted, without imposing a blanket physical sample requirement. Final copper, drill, Gerber and mechanical review remain open. The current governing records are `verification/gate-b-review.md`, `verification/independent-review.md` and `fabrication/rule-target.md`.

## Verified facts

- The requested fabrication class is two-layer FR-4, nominal 1.6 mm, 1 oz copper.
- The release dates 24 and 25 October 2026 fall on Saturday and Sunday. The desired assembly date, 31 October, is also Saturday.
- The Netherlands changes from CEST to CET on Sunday 25 October 2026. There is no Dutch national public holiday from 26 through 30 October.
- Four OPA1656IDR parts are reserved. TI identifies this exact MPN as an 8-pin SOIC `D` package.
- Exact stock identities now include all capacitors, diodes, terminal block, BNC, and op amps: Vishay MKP1837310011/MKP1837368011 film capacitors, KYOCERA AVX SR215A102FARTR1 C0G, KEMET C315C104K5R5TA bypass capacitors, Panasonic EEU-FR1H100 bulk capacitors, onsemi 1N4148 DO-35 diodes, Molex 39543-0003 terminal block, Amphenol RF 031-5431-10RFX BNC, and TI OPA1656IDR. Drawing-derived footprints and 1:1 checks remain required.
- The archived physical design specifies four dual OPA1656 packages for seven active channels, external ±15 V rails, and a 10 kΩ linear potentiometer across VFINAL-to-ground with the wiper as the high-impedance adjustable output.
- Alps Alpine `RK09K1130A5R` is the recommended potentiometer: 10 kΩ linear 1B, single gang/turn, no detent, 0.05 W, 20 mm × 6 mm knob shaft, PC pins and board locks. The current Alps drawing is explicit, and KiCad's official `Potentiometer_Alps_RK09K_Single_Vertical` footprint lists this MPN. DigiKey Netherlands showed 471 in stock at €1.46 excluding VAT on 22 October 2026. No order was placed.
- TinyTronics `RV09-10K` (SKU 001720) remains a local alternative. Cached retailer text claims Alpha RV09 / ALPS RK09K compatibility, but exact dimensions are unavailable during the site outage. It cannot replace the exact Alps MPN on the released footprint until a sample or dimensioned drawing verifies holes, board locks, and pins.
- The fixed resistor implementation requires 44 physical resistors and preserves every requested series/parallel network. R11's 2 kΩ || 100 kΩ nominal equivalent is 1,960.784 Ω. Fourteen YAGEO RT0805 exact MPNs plus stocked Vishay Dale TNPW080547K0BEEA for 47 kΩ are selected at 0.1% and 25 ppm/°C. The specified order quantity is 74 pieces, providing two spares per value. The Vishay substitution avoids the backorder-only YAGEO 47 kΩ line without changing value, tolerance, tempco, or footprint.
- Molex drawing SD39543-003 rev B2 specifies Ø1.20 mm holes at 5.00 mm pitch and a 15.0 × 9.5 mm body. The previously asserted centered 4.75 mm row datum was not independently substantiated. A conservative ±10 mm depth courtyard removes dependence on that assumption and passed placement review.
- The BNC pattern and handedness are independently verified from the original manufacturer drawing: two Ø0.89 mm signal/shell pins and two Ø2.01 mm mounting posts. Final mating/access and drill export checks remain required.
- TI specifies OPA1656 quiescent current at 3.9 mA/channel typical and 5 mA/channel maximum across temperature. Four dual packages therefore account for 31.2 mA typical and 40 mA maximum quiescent current per rail before signal-load current; the first-power procedure uses a 60 mA limit per rail.
- AISLER publishes a compatible 2-layer 1.6 mm/35 µm ENIG class and advertises one-business-day bare-board manufacture; the live delivery date is not known.
- Eurocircuits PCB Proto advertises 2- or 3-working-day bare boards and states that lead time is working days and ends at shipment. Its public PCB Proto thickness is 1.55 mm, so it is not an exact 1.6 mm match without accepting that service specification.
- JLCPCB publicly supports 2-layer FR-4 at 1.6 mm and 1 oz. Its build time starts at physical production; weekend payment and shipping-center pickup rules can delay dispatch.
- PCBWay's “24-hour Express” is production-start to production-completion, not payment to delivery. Shipping time remains additional.
- No design files were uploaded and no quote or order was placed.
- The optimized simulation result was about 90.8 dB SFDR. Separately, the archived breadboard spectrum recorded 10,052.83 Hz and an 88.79 dB fundamental-to-H3 cursor separation near full output. It is historical hardware evidence, but it includes the acquisition setup and lacks an independent setup-residual calibration. No new-PCB measurement exists.

## Assumptions requiring confirmation

- Boards will be ordered bare and assembled locally by hand.
- Green solder mask and white legend are acceptable.
- A lead-free surface finish is required; the final choice between lead-free HASL and ENIG is not yet made.
- If the selected Alps MPN is used, its current manufacturer drawing and official KiCad footprint will receive a final 1:1 review. If the local TinyTronics option is used instead, its exact geometry and terminal numbering require a sample/drawing check.
- Every selected resistor MPN has a cut-tape distributor catalog entry. Live stock was present for the checked lines except the original YAGEO 47 kΩ choice, which was replaced by the stocked Vishay part; recheck all quantities at order time.
- The word “delivery” means physical receipt in the Netherlands, not the supplier's shipment date.

## Proposals

- Prefer a European quick-turn quote first: AISLER Blitz for an exact nominal 1.6 mm/35 µm class, then Eurocircuits if its 1.55 mm service is acceptable. Obtain live dated shipment and delivery estimates on Monday 26 October if release occurs over the weekend.
- Treat Asian 24-hour production services as contingency options because production time excludes international transit and weekend pickup can add delay.
- Use unique physical references for each resistor element while grouping them by logical resistor network in the schematic and BOM.
- Use a controlled first-power procedure and a coherent-sampling SFDR method. Hardware goal is ≥80 dBc; acceptance threshold is ≥75 dBc. The test setup must demonstrate adequate residual-spur margin.

## Open issues and release blockers

1. Gate B schematic/routing approval is recorded. Final board approval remains open. Internal Gerbers may be generated for review, but no manufacturing release is allowed before all final checks and user approval.
2. The recovered rails are ±15 V and a 60 mA-per-rail first-power limit is defined. The released PCB/schematic must still pass rail mapping and internal-node review before power-up.
3. The exact Alps potentiometer and footprint are selected and documented; final footprint-revision/1:1 review remains. Choosing the local TinyTronics option instead reopens its geometry and pin-mapping blocker.
4. All reserved component MPNs are now known. Drawing/1:1 checks remain open, especially the custom BNC, terminal, film-capacitor, and Alps potentiometer footprints; using the unbranded TinyTronics alternative additionally requires its own sample or dimensioned drawing.
5. Four dual op amps/seven active channels are recovered; final footprint/pin-map review still depends on the approved schematic and PCB.
6. Resistor MPNs and stress calculations are defined. Stock must be rechecked at order time and the 0805 land pattern must pass PCB review.
7. Board outline, mounting/enclosure constraints, connector clearances, and maximum component height are not available in this workstream.
8. The selected manufacturer, surface finish, quantity, courier service, quoted shipment date, and quoted Netherlands delivery date are not approved.
9. The SFDR measurement bandwidth, output amplitude/load, warm-up, and available analyzer residual performance are not specified.

## Done

- Captured reserved-stock MPNs and the remaining physical-fit gates.
- Expanded and counted all requested resistor networks without changing their nominal values.
- Produced a draft BOM and component fit-release gate.
- Produced a no-Gerber manufacturing checklist and an official-source supplier/calendar assessment.
- Produced assembly, blocked power-up, functional-test, and valid SFDR measurement templates.

## Not done

- No custom footprint has completed the required 1:1 physical review. The exact Alps potentiometer removes the documentation blocker; the unbranded TinyTronics alternative remains sample/drawing-gated.
- The resistor MPN set and exact Alps potentiometer are selected, but nothing has been ordered.
- No PCB plots, Gerbers, drill files, quotes, uploads, or orders were made.
- No delivery date is guaranteed.
- No new PCB was assembled or powered, and no new-PCB SFDR result exists. The archived breadboard's 88.79 dB cursor result remains historical evidence only.

Supporting files:

- `../bom/README.md`
- `../bom/draft_bom.csv`
- `../fabrication/manufacturing-checklist.md`
- `../assembly/assembly-and-test.md`

