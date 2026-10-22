# Draft BOM and component release gate

Status: **DRAFT — PART LIST DEFINED; NOT READY TO ORDER OR FABRICATE**  
Scope: prototype oscillator PCB, bare-board fabrication followed by hand assembly.

The machine-readable draft is in `draft_bom.csv`. A row marked `BLOCKED` must not be converted into a purchase or footprint commitment until its missing data is resolved against the physical stock or an official manufacturer drawing.

## Verified stock facts

The following quantities and exact identities were supplied for reserved stock.

| Item | Reserved | Known exact identity | Release state |
|---|---:|---|---|
| Dual op amp | 4 fitted | Texas Instruments OPA1656IDR, SOIC (D), 8 pins | Four dual packages implement seven active channels; pin mapping and land pattern still require PCB review |
| 10 nF, 1% polypropylene capacitor | 4 | Vishay MKP1837310011, 160 VDC, radial 5 mm pitch | Identified; custom/verified footprint required |
| 1 nF, 1% C0G capacitor | 1 | KYOCERA AVX SR215A102FARTR1, 50 V, radial 5.08 mm | Identified; drawing/1:1 footprint check required |
| 68 nF, 1% polypropylene capacitor | 1 | Vishay MKP1837368011, 160 VDC, radial 5 mm pitch | Identified; custom/verified footprint required |
| 100 nF X7R capacitor | 8 fitted + 2 spare | KEMET C315C104K5R5TA, 50 V, radial 2.54 mm | Identified; footprint check required |
| 10 uF, 50 V electrolytic capacitor | 2 fitted + 2 spare | Panasonic EEU-FR1H100, radial 2.0 mm pitch, Ø5 × 11 mm | Identified; polarity/footprint check required |
| Switching diode | 2 | onsemi 1N4148, DO-204AH/DO-35 axial | Identified; lead-span choice/1:1 check required |
| Three-position screw terminal | 1 | Molex 39543-0003, 3 circuits, 5.00 mm pitch | Identified; drawing-derived footprint required |
| Right-angle PCB BNC | 1 | Amphenol RF 031-5431-10RFX, 50 Ω, right-angle THT rear-mount bulkhead jack | Identified; drawing-derived footprint required |
| PCB potentiometer | 1 to buy | **Selected fallback:** Alps Alpine RK09K1130A5R, 10 kΩ linear single-turn vertical THT | Manufacturer-documented and supported by the KiCad Alps RK09K footprint; current drawing/1:1 review required |
| Local potentiometer option | 0 fitted unless verified | TinyTronics `RV09-10K`, SKU 001720: cached listing says 10 kΩ linear and RV09/RK09K-compatible | Exact retailer geometry unavailable; do not substitute into the Alps footprint without sample/drawing verification |

Texas Instruments identifies OPA1656IDR as the 8-pin SOIC `D` package. The proposed KiCad footprint is `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm`; it must be checked against the current TI D-package drawing and the PCB pad geometry before release. Four dual devices are fitted: seven channels are active and the eighth must be terminated as the released schematic specifies.

The exact stock line is now confirmed as onsemi `1N4148` (Mouser 512-1N4148). onsemi specifies DO-204AH/DO-35 bulk axial. Select the final horizontal lead span to suit stress-free forming of the physical parts and verify at 1:1; do not replace it with a surface-mount 1N4148-family footprint.

The Vishay MKP1837 drawing gives 0.5 mm leads on 5.0 ± 0.4 mm pitch. MKP1837310011 has a nominal 5.5 × 7.0 × 7.5 mm body; MKP1837368011 has a nominal 7.5 × 9.0 × 7.5 mm body (W × H × L). Vishay requires envelope allowance for its maximum dimensions; do not use a smaller generic film-capacitor courtyard.

Molex 39543-0003 is a 15.0 mm-long, three-position vertical PCB terminal block with horizontal wire entry, 5.00 mm pitch, 9.5 mm body depth, and 3.60 ±0.25 mm tails. Official drawing SD39543-003 rev B2 specifies three Ø1.20 mm PCB holes. The initially reported 4.75 mm centered row datum has not been independently established visually. The accepted footprint conservatively reserves 9.5 mm full body depth on both sides of the pin row plus 0.5 mm margin, and 0.75 mm width-end margins. The centered Fab body sketch is illustrative. The actual conservative placement envelope passed independent review.

Amphenol 031-5431-10RFX requires its exact pattern and is not interchangeable with a generic BNC footprint. From the manufacturer drawing, with the center contact at `(0,0)`, the second small pin is at `(-2.54,0)` and the two mounting posts are at `(-5.08,-5.08)` and `(+5.08,-5.08)` mm, where negative y points toward the mating face. Use Ø0.89 mm holes for the two small pins and Ø2.01 mm holes for the mounting posts. The body envelope is 14.4 mm wide × 15.6 mm high and 34.8 mm overall length. The body-front datum is 20.7 mm from the mating tip; the mounting-post row is 7.87 mm behind that datum, making the body front 12.95 mm ahead of the signal-pin row. Verify footprint view/handedness and panel/board-edge placement against a printed 1:1 plot and the physical part before release.

The recommended build choice is Alps Alpine `RK09K1130A5R`: 10 kΩ, linear `1B` taper, single gang, one turn, no detent, 0.05 W, ±20%, 280° rotation, top adjustment, 20 mm-long × 6 mm-diameter knob shaft, PC pins and board locks. Alps drawing No. 3 gives a 9.8 mm-wide body and three Ø1.0 mm terminal holes in a straight line at 2.5 mm spacing. KiCad's official `Potentiometer_THT:Potentiometer_Alps_RK09K_Single_Vertical` footprint explicitly lists `1130A5R` among its supported parts. Its current source places pins 1/2/3 at `(0,0)`, `(0,2.5)`, `(0,5.0)` mm with Ø1.0 mm drills and the two mechanical slots at `(7,-1.9)` and `(7,6.9)` mm with 2.1 × 1.8 mm oval drills. Compare the installed footprint revision with the current Alps drawing and print it at 1:1 before release.

DigiKey Netherlands part `4809-RK09K1130A5R-ND` showed 471 in stock at €1.46 each excluding VAT (€1.7666 including VAT) on 22 October 2026. This gives a concrete, orderable fallback while the local retailer is offline; no order has been placed.

Alps specifies this family for voltage adjustment and asks for output-side impedance greater than 100 times the potentiometer resistance to limit wiper-contact error. For 10 kΩ, keep the connected measurement input above 1 MΩ; the recovered high-impedance output use satisfies this with an instrument input greater than 1 MΩ.

The user explicitly approved the exact Alps MPN. TinyTronics `RV09-10K`, SKU 001720 is an unapproved alternate only. Cached compatibility text does not establish matching holes, board locks or pin numbering; the live site was unavailable. The footprint remains tied to Alps. Electrical wiring is unchanged: end terminals across VFINAL and ground, wiper to the high-impedance adjustable output. Drawing 3 confirms pin 2 as wiper but the inspected sources do not establish which endpoint corresponds to clockwise travel; check adjustment direction during assembly, with no directional silkscreen claim.

KYOCERA AVX SR215A102FARTR1 is a 1 nF ±1%, 50 V C0G/NP0 radial SkyCap. The SR21 outline is 5.08 mm long by 3.18 mm thick with 7.62 mm maximum seated height and 5.08 mm lead spacing. KEMET C315C104K5R5TA is 100 nF ±10%, 50 V X7R radial with 3.81 × 3.14 × 2.54 mm maximum body dimensions, 2.54 ±0.78 mm lead spacing, and 0.51 mm leads. Panasonic EEU-FR1H100 is 10 µF ±20%, 50 V polar radial, Ø5 × 11 mm, 2.0 mm lead spacing, and 0.5 mm leads.

## Fixed resistor implementation

The following networks preserve the requested nominal values. No substitution, simplification, or single-value replacement is authorized without an impact review covering ratio error, noise, distortion, temperature drift, voltage coefficient, power, and layout parasitics.

| Logical resistor | Physical network | Nominal result |
|---|---|---:|
| R1, R2, R3, R4 (each) | 1 kΩ + 330 Ω + 270 Ω + 47 Ω in series | 1,647 Ω |
| RG | 10 kΩ | 10,000 Ω |
| RF | 47 kΩ + 1 kΩ in series | 48,000 Ω |
| R5, R7 (each) | 100 kΩ + 20 kΩ + 10 kΩ in series | 130,000 Ω |
| R6, R8 (each) | 300 kΩ + 20 kΩ + 4.7 kΩ + 200 Ω + 100 Ω in series | 325,000 Ω |
| R9, R10 (each) | 1 kΩ + 680 Ω + 220 Ω in series | 1,900 Ω |
| R11 | 2 kΩ in parallel with 100 kΩ | 1,960.784 Ω |
| R12 | 1 kΩ | 1,000 Ω |

Required fitted resistor count is 44:

| Nominal value | Fitted quantity |
|---:|---:|
| 1 kΩ | 8 |
| 330 Ω | 4 |
| 270 Ω | 4 |
| 47 Ω | 4 |
| 10 kΩ | 3 |
| 47 kΩ | 1 |
| 100 kΩ | 3 |
| 20 kΩ | 4 |
| 300 kΩ | 2 |
| 4.7 kΩ | 2 |
| 200 Ω | 2 |
| 100 Ω | 2 |
| 680 Ω | 2 |
| 220 Ω | 2 |
| 2 kΩ | 1 |

### Selected resistor procurement set

Use YAGEO RT-series thin-film 0805 parts except the 47 kΩ RF element, for which use the stocked Vishay Dale TNPW part shown below. Every selection is ±0.1% and ±25 ppm/°C. YAGEO RT0805 is rated 0.125 W at 70 °C and 150 V maximum continuous working voltage; the selected Vishay part meets or exceeds the required normal-operation stress. The common PCB land pattern is `R_0805_2012Metric`. Distributor catalog/cut-tape records were checked on 22 October 2026; the original YAGEO 47 kΩ selection was backorder-only at DigiKey and was replaced by the in-stock Vishay part. Stock is volatile, so recheck immediately before ordering. The order quantities below include two spare pieces per value, giving 74 planned for purchase for 44 fitted; none have been ordered.

| Value | Selected MPN | Fitted | Order quantity |
|---:|---|---:|---:|
| 47 Ω | RT0805BRD0747RL | 4 | 6 |
| 100 Ω | RT0805BRD07100RL | 2 | 4 |
| 200 Ω | RT0805BRD07200RL | 2 | 4 |
| 220 Ω | RT0805BRD07220RL | 2 | 4 |
| 270 Ω | RT0805BRD07270RL | 4 | 6 |
| 330 Ω | RT0805BRD07330RL | 4 | 6 |
| 680 Ω | RT0805BRD07680RL | 2 | 4 |
| 1 kΩ | RT0805BRD071KL | 8 | 10 |
| 2 kΩ | RT0805BRD072KL | 1 | 3 |
| 4.7 kΩ | RT0805BRD074K7L | 2 | 4 |
| 10 kΩ | RT0805BRD0710KL | 3 | 5 |
| 20 kΩ | RT0805BRD0720KL | 4 | 6 |
| 47 kΩ | Vishay Dale TNPW080547K0BEEA | 1 | 3 |
| 100 kΩ | RT0805BRD07100KL | 3 | 5 |
| 300 kΩ | RT0805BRD07300KL | 2 | 4 |

The stress review uses actual network placement, rather than applying the full 30 V rail-to-rail supply to every element:

- For any low-value series chain with at most 15 V peak sinusoidal voltage across the complete chain, the 1.647 kΩ timing chain dissipates 68.3 mW total; its largest 1 kΩ element dissipates 41.5 mW average. The 1.9 kΩ chain dissipates 59.2 mW total; its 1 kΩ element dissipates 31.2 mW. Both are below 0.125 W with margin. Confirm the complete timing-chain peak voltage is below 15 V during bring-up; the circuit topology and recovered approximately 5 Vpp output support that normal-operation bound.
- At a deliberately conservative 15 V peak op-amp output, gain 4.8 puts about 11.875 V peak across RF. The 47 kΩ element dissipates about 1.4 mW average. RG dissipates below 0.5 mW.
- With 15 V peak at the driver of R11/R12, the 2 kΩ branch of R11 dissipates about 24.7 mW average and R12 about 12.8 mW. These are the largest calculated output-divider element stresses.
- Even an intentionally severe 30 V DC across an entire limiter chain gives only 6.9 mW total in a 130 kΩ chain and 2.8 mW total in a 325 kΩ chain.

These checks cover normal operation. A wiring fault that forces rail-to-rail voltage across a low-value chain is handled by current-limited bring-up, not treated as a continuous resistor operating condition.

Series elements must be placed consecutively in the signal path with short connections. The two R11 elements must share the same two electrical nodes. The BOM and schematic should use unique physical reference designators for every element while retaining the logical-network name in a dedicated field or schematic group.

## Component fit-release procedure

1. Retain stock bag/label identification; photographs beside a metric ruler are a useful supplementary receiving record.
2. Record manufacturer, full ordering code, dielectric/tolerance, voltage rating, lead pitch or package code, body dimensions, and height.
3. A 1:1 physical placement check is recommended when the part is available, and required only where a consequential fit ambiguity cannot be resolved from exact drawings.
4. Compare hole sizes, pad dimensions, courtyard, polarity/pin-1, board-edge datum, and connector mating clearance with the official drawing.
5. For the exact Alps part, verify the current manufacturer drawing against the footprint at 1:1 and confirm terminal numbering/rotation on receipt with a DMM. Connect its end terminals across VFINAL and ground and its wiper to the BNC output; keep the measurement/load high impedance. A physical sample or dimensioned drawing is mandatory before substituting the unbranded TinyTronics option.
6. Update `draft_bom.csv` to `VERIFIED` only after the schematic symbol, pin mapping, and footprint are jointly reviewed.

## Official package references

- TI OPA1656 product and package page: https://www.ti.com/product/OPA1656/part-details/OPA1656IDR
- TI OPA165x datasheet, including D-package drawing: https://www.ti.com/lit/ds/symlink/opa1656.pdf
- onsemi 1N4148/1N914 family datasheet: https://www.onsemi.com/pdf/datasheet/1n914-d.pdf
- Vishay MKP1837 datasheet: https://www.vishay.com/docs/26017/mkp1837.pdf
- Molex 39543-0003 product page: https://www.molex.com/en-us/products/part-detail/395430003
- Molex 39543 drawing SD39543-003: https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/395/39543/395430002_sd.pdf?inline=
- Amphenol RF 031-5431-10RFX product page: https://www.amphenolrf.com/en-us/part/031-5431-10rfx/1887/
- TinyTronics RV09-10K local option: https://www.tinytronics.nl/nl/componenten/weerstanden/potmeters/10k-potmeter-rv09
- ALPS Alpine RK09K/RK09D primary family drawing: https://tech.alpsalpine.com/cms.media/product_catalog_rv_02_rk09k_rk09d_en_26d4cb95ac.pdf
- Alps Alpine RK09K1130A5R primary product page: https://tech.alpsalpine.com/e/products/detail/RK09K1130A5R/
- DigiKey Netherlands stock/price page: https://www.digikey.nl/en/products/detail/alps-alpine/RK09K1130A5R/21721633
- KiCad official Alps RK09K vertical footprint: https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/Potentiometer_THT.pretty/Potentiometer_Alps_RK09K_Single_Vertical.kicad_mod
- YAGEO RT0805 part-specific specification example (family construction/rating): https://yageogroup.com/component-documentation/download/specsheet/RT0805BRD07100RL
- Vishay TNPW e3 resistor family datasheet: https://www.vishay.com/docs/28758/tnpw.pdf
- KYOCERA AVX SR-series drawing: https://datasheets.kyocera-avx.com/SR-Series.pdf
- KEMET C315C104K5R5TA specification: https://search.kemet.com/component-documentation/download/specsheet/C315C104K5R5TA
- Panasonic FR-series catalog: https://industrial.panasonic.com/cdbs/www-data/pdf/RDF0000/ast-ind-152837.pdf

