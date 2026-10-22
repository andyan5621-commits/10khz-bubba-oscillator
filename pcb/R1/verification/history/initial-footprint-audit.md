# Independent footprint audit

22 October 2026. Overall footprint gate: **FAIL / incomplete**. These findings refer to the inspected placement study and native export, not future revisions.

## Assignment completeness

The corrected native netlist has only four assigned footprints: U1–U4 use `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm`. The other 65 components are unassigned. The board has only the four ICs and 16 capacitors, without electrical net assignments. No resistor, diode, power connector, BNC or pot footprint is yet implemented in that board. Zero DRC violations on that skeleton do not clear the board gate.

## Reserved IC and capacitor geometry

| Part | Actual footprint inspected | Independent assessment |
|---|---|---|
| OPA1656IDR | Standard SOIC-8 3.9×4.9, 1.27 pitch, numbered counterclockwise from top-left pin1 | Nominal package and pin-numbering match TI D/SOIC. Pads 1.95×0.60 at x=±2.475; suitable draft pattern. Final rotation, pin1 legend and board net assignments still need audit. |
| MKP1837310011 | Custom body7.5×5.5, pitch5, hole0.85, pad1.65 | Nominal plan dimensions match manufacturer. Vishay additionally specifies pitch±0.4, body-envelope tolerances and eccentricity. Check stocked lead form and finished-hole fit. |
| MKP1837368011 | Custom body7.5×7.5, pitch5, hole0.85, pad1.65 | Nominal plan dimensions match manufacturer. Height9mm is consistent; use drawing tolerances for enclosure and courtyard. |
| SR215A102FARTR1 | Custom body5.08×3.18, pitch5.08, hole0.85, pad1.65 | Nominal body/lead spacing matches SR21 family, 0.508mm lead. Formed leads and seating-plane details require actual fit check. |
| C315C104K5R5TA | Custom body3.81×2.54, pitch2.54, hole0.85, pad1.60 | Manufacturer exact-MPN sheet confirms these body and nominal-pitch values. Lead diameter reaches0.61mm; pitch tolerance±0.78mm means leads can require gentle forming. Do not assume all stock drops into nominal pitch untouched. |
| EEU-FR1H100 | Standard radial D5 pitch2 | Manufacturer catalog supports D5×11, lead0.5, pitch2. Corrected schematic has proper ±rail polarity; final pad1 positive mapping must survive board import. |

Primary documents: [TI](https://www.ti.com/lit/ds/symlink/opa1656.pdf), [Vishay MKP1837 drawing](https://www.vishay.com/docs/26017/mkp1837.pdf), [KYOCERA AVX SR series](https://datasheets.kyocera-avx.com/SR-Series.pdf), [KEMET/Yageo exact MPN sheet](https://yageogroup.com/download/specsheet/C315C104K5R5TA), [Panasonic catalog](https://industrial.panasonic.com/content/data/CP/PDF/S_Alm_A_cap_catalog_am.pdf).

## Amphenol BNC: exact drawing recovered and visually inspected

The [manufacturer outline drawing hosted by Farnell](https://www.farnell.com/cad/1649157.pdf) is linked directly by the distributor's exact031-5431-10RFX product page. The drawing itself is31-5431-10RFX, revisionC, sheet2/2, with a2011 corrected-view revision. The local original is `drawings/amphenol-farnell.pdf`; the rendered image actually inspected is `drawings/amphenol.png`. The leading zero is the current ordering-code style; this is not the different31-5486 drawing.

The drawing's pattern has two Ø2.01mm mounting holes separated10.16mm, and two Ø0.89mm contact holes separated2.54mm. The contact-hole row is5.08mm behind the mounting-hole row. One contact hole is on the midpoint/connector axis and is the centre signal contact; the other is the shell contact.

Convenient proposed coordinate system, with the signal contact at origin and negativeY toward the mating face:

| Pad function | X mm | Y mm | Drawing hole mm |
|---|---:|---:|---:|
| Signal, intended schematicJ2.1 | 0 | 0 | 0.89 |
| Shell, intended schematicJ2.2 | -2.54 | 0 | 0.89 |
| Mounting fork | -5.08 | -5.08 | 2.01 |
| Mounting fork | +5.08 | -5.08 | 2.01 |

The negativeX shell side follows the shown rear-contact/mounting-pattern projection. Top-versus-bottom drawing handedness must be reconciled before final footprint approval; a second unambiguous manufacturer view or a sample can resolve this. Mounting forks are mechanical pins in a plastic housing: their electrical connection to shell is not established by this outline. Do not silently assign them to ground. A footprint may reserve appropriate holes without asserting an unevidenced electrical connection.

Other drawing dimensions: body width14.4mm, overall height15.6mm, connector centreline8.56mm above its seating datum, overall length34.8mm. The front body datum is20.7mm behind the mating tip; the mounting row is7.87mm behind that datum, implying the front body datum lies12.95mm toward the mating face from the signal row. These reference dimensions define a candidate envelope; they do not establish the user's panel/board-edge requirement. Maximum panel thickness5mm. Nut and access clearance must be reserved.

The current official Amphenol asset could be read via the web service but direct download was denied. The named manufacturer drawing above was successfully downloaded and visually inspected. No claim is made that its older revision is byte-identical to the current official asset.

## Molex supply connector

The exact [user-provided original drawing URL](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/395/39543/395430002_sd.pdf?inline=) returns SD-39543-003B2 and explicitly lists39543-0003. Text extraction verifies three pins on5.00mm pitch,15.0mm body length,10.0mm span between first/last pins, and recommendedØ1.20mm PCB holes. The text also contains9.5mm body-depth and14.5mm height dimensions. The draft BOM's1.40mm manufacturer-hole claim is unsupported; do not use39543-3003 as a substitute source.

The original host repeatedly reset/timed out direct downloads; an alternate mirror required a browser challenge. A visual local drawing could therefore not be verified in this pass. The depth offset relative to pin row and wire-entry orientation remain open. Do not claim a completed custom Molex footprint solely from the parsed dimensions.

## Remaining gate

No approved pot land pattern is available, and its physical terminal numbering/rotation sense is unknown. The electrical capture's pin1=VFINAL,pin2=wiper,pin3=GND is correct for the planned convention; it must be reconciled with the actual chosen pot. Resistor package and diode lead-span selections also need final artifact checks. Assigning footprint names is not by itself evidence of mechanical verification. A physical sample is not a blanket approval requirement where an exact manufacturer drawing fully establishes geometry and connection; the unresolved points above identify actual evidence gaps.
