# Bare-board manufacturing release checklist

Status: **DRAFT — INTERNAL EXPORTS FOR REVIEW ONLY; NO MANUFACTURING RELEASE OR ORDER BEFORE ALL GATES PASS AND USER APPROVAL**

## Intended fabrication class

The requested target is a two-layer rigid FR-4 PCB, nominal 1.6 mm finished thickness and 1 oz finished outer copper. Green solder mask and white legend are the low-risk default proposal. Surface finish remains a cost/schedule choice; lead-free HASL is acceptable for ordinary SOIC and through-hole assembly, while ENIG offers flatter pads. Confirm the finish in the approved order specification.

Do not silently map “1.6 mm / 1 oz” onto a manufacturer's similarly named pool. For example, Eurocircuits PCB Proto publicly lists 1.55 mm board thickness and 18 µm base outer copper; its copper terminology distinguishes base from finished copper. AISLER publishes a 2-layer 1.6 mm, 35 µm ENIG class. JLCPCB lists 1.6 mm and 1 oz finished outer copper as available options. The order record must retain the manufacturer's exact wording and tolerances.

## Release gates

### Electrical and schematic

- [ ] Final schematic has passed ERC with every intentional exception documented.
- [ ] All OPA1656 units, power pins, supply decouplers, connector pins, diode polarity, electrolytic polarity, and potentiometer terminals are explicitly mapped.
- [ ] Final positive and negative rail voltages are approved and within the OPA1656 range and every passive rating.
- [ ] Each logical resistor network implements the exact physical series/parallel elements listed in `../bom/README.md`.
- [ ] All 44 fitted resistor elements use the selected 0805 MPN/value mapping; order quantities total 74 including two spares per value.
- [ ] The potentiometer's passive-divider topology, value, taper, wiper behavior, and safe end stops are approved.
- [ ] Test points exist for both rails, ground, oscillator nodes needed for bring-up, and output.

### Component and mechanical fit

- [ ] Every fitted BOM row has an approved manufacturer part number.
- [ ] Every footprint was checked against the exact official package drawing. A 1:1 physical print is a useful supplementary check for available stock; require it only where a consequential geometry ambiguity remains unresolved by drawings.
- [ ] Molex 39543-0003 uses three Ø1.20 mm holes at 5.00 mm pitch; wire entry, screwdriver access, body depth, and pin order are confirmed.
- [ ] Amphenol 031-5431-10RFX uses the exact two-Ø0.89/two-Ø2.01 pattern recorded in the BOM; view handedness, board-edge datum, mating clearance, shield connection, and mechanical retention are confirmed.
- [ ] Alps RK09K1130A5R is checked against drawing No. 3 and the installed `Potentiometer_Alps_RK09K_Single_Vertical` revision, including the retention-slot fit. No unverified TinyTronics substitution is included.
- [ ] Electrolytic diameter/height and film-capacitor body/courtyard clearances are confirmed.
- [ ] Board outline, mounting holes, enclosure constraints, keepouts, and maximum component height are approved.

### Layout and manufacturability

- [ ] Final board review is signed off before fabrication plots are released. Internal review exports are marked unreleased and regenerated after any correction.
- [ ] DRC is clean using rules no looser than the selected manufacturer's current published capabilities.
- [ ] Ground return paths, decoupling loop areas, sensitive high-impedance nodes, output-current paths, and BNC shield current paths received an analog-layout review.
- [ ] Series resistor chains are physically consecutive and R11's two elements are truly parallel.
- [ ] Copper-to-edge, annular rings, finished holes, slots, mask dams, legend widths, and legend-to-pad clearances meet the selected service.
- [ ] No legend covers pads; polarity, pin 1, connector function, rail polarity, board name, and revision are readable.
- [ ] Unconnected copper islands are removed or intentionally tied.
- [ ] Zone fills are regenerated; final DRC is rerun after filling.
- [ ] 3D/mechanical review includes connector mating and tool access.

### Fabrication package, only after approval

- [ ] Generate Gerber X2 or manufacturer-supported Gerbers from the approved commit/revision.
- [ ] Include top copper, bottom copper, top mask, bottom mask, top legend, bottom legend only if used, and Edge.Cuts.
- [ ] Generate Excellon plated and non-plated drill data with matching origin and units.
- [ ] Do not include fabrication, courtyard, user-drawing, or assembly layers as copper/legend outputs.
- [ ] Inspect the plotted archive in an independent Gerber viewer; compare drill and copper alignment, outline, mask openings, text, and board extents.
- [ ] Record plot settings, CAD version, git/source revision or file hashes, DRC report, approved BOM revision, and reviewer/date.
- [ ] Use the manufacturer's online analysis only after internal approval; stop if it changes geometry or reports ambiguous data.
- [ ] Order bare boards only. Do not request assembly unless a separately reviewed CPL/BOM package and component logistics exist.

## Expedited supplier and calendar assessment

### Calendar facts

- 24 October 2026 is Saturday; 25 October is Sunday; 31 October is Saturday.
- The Netherlands changes from summer time to winter time at 03:00 on Sunday 25 October 2026. Record cutoffs in the supplier's stated timezone.
- The Dutch government lists no national public holiday during 26–30 October 2026. Courier and supplier availability still requires confirmation.

### Shortlist

| Supplier/service | Officially published fact | Weekend implication for a 24–25 Oct release | Assessment for Netherlands receipt and assembly by 31 Oct |
|---|---|---|---|
| AISLER, 2-layer Blitz | AISLER states one-business-day manufacture for Beautiful Boards; its published 2-layer class includes 1.6 mm/35 µm ENIG. A 2024 official announcement says 24 h manufacture required ordering before 06:00 CET. | A weekend design release does not itself start a business-day build. Obtain the live checkout date early Monday 26 Oct CET. | Best geographic candidate because manufacture is in Europe, but delivery date must be confirmed in the live quote. Do not promise 31 Oct. |
| Eurocircuits, PCB Proto | Bare boards are advertised in 2 or 3 working days, with shorter calculator options. Working days are Monday–Friday; lead time starts only with complete/correct data, and the calculated date is a shipment date. | Weekend days do not count. A clean weekend launch would ordinarily put working-day production into 26–28 Oct, depending on selected service and acceptance. | Plausible only with a live expedited quote and courier date. Note its standard Proto build is 1.55 mm rather than exactly 1.6 mm. |
| JLCPCB | 1.6 mm/1 oz 2-layer FR-4 is supported. Build time starts with physical production, not payment. Orders paid after Saturday 18:00 GMT+8 or on public holidays wait for the next business day. Orders reaching its shipping center after 11:00 Saturday dispatch Monday because there is no Saturday-afternoon/Sunday pickup. | Release timing can lose both production-start and carrier-pickup time. International transit is additional. | Technically compatible, but high schedule risk for a 31 Oct Netherlands assembly date. |
| PCBWay, 24-hour Express | Official help says “24-hour” runs from production start to production completion, not from payment; payment after 18:00 GMT+8 can postpone production by one day. Shipping is separate. | Weekend/holiday notices and the GMT+8 cutoff must be checked at order time. | Technically possible, but international transit makes the 31 Oct target high risk. |

Recommended scheduling action: finish review before the weekend if possible. If approval only occurs on 24–25 October, prepare the release archive but obtain live dated quotes from AISLER and Eurocircuits first thing Monday 26 October. Select only a quote that explicitly shows both shipment and delivery estimates to the Netherlands. Treat 31 October as a target, never a guarantee, and keep a contingency assembly slot after that date.

No board data has been uploaded and no quote or order has been placed.

## Official sources checked 22 October 2026

- AISLER home/service claims: https://aisler.net/en-US
- AISLER 2-layer 1.6 mm, 35 µm ENIG rules: https://community.aisler.net/t/2-layer-1-6mm-35-m-enig-design-rules/3732
- AISLER lead-time announcement: https://community.aisler.net/t/we-reduced-our-pcb-leadtime-by-up-to-a-day-enabling-rapid-prototyping/3577
- Eurocircuits PCB Proto parameters: https://www.eurocircuits.com/services/pcb-proto/
- Eurocircuits lead-time definition: https://www.eurocircuits.com/lead-time/
- Eurocircuits weekend-aware shipment-date explanation: https://www.eurocircuits.com/shipment-date/
- JLCPCB capabilities: https://jlcpcb.com/capabilities/Capabilities
- JLCPCB build-time definition and cutoff: https://jlcpcb.com/help/article/what-is-the-build-time
- JLCPCB weekend shipping pickup: https://jlcpcb.com/help/article/when-will-my-order-be-shipped
- PCBWay express-time definition and cutoff: https://www.pcbway.com/helpcenter/lead_time/When_will_express_order_be_produced_.html
- Dutch 2026 public holidays: https://www.government.nl/themes/work/working-hours/question-and-answer/work/public-holidays-in-the-netherlands
- Dutch 25 October 2026 clock change: https://www.rijksoverheid.nl/themas/overheid-en-democratie/zomertijd-wintertijd/vraag-en-antwoord/klok-verzetten-nederland

