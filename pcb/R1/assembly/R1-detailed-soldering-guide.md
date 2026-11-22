# R1 oscillator PCB — detailed soldering and first-power guide

Prepared 22 October 2026 for the released R1 / R1-review-03 board, 95 × 79 mm, four OPA1656IDR packages, ±15 V supplies, and Alps RK09K1130A5R amplitude control. This is an assembly procedure, not a claim that the PCB has been physically tested. Build and verify **one board first**; your three bare PCBs do not imply that you have three component sets.

Board/serial: __________  Assembler: __________  Date: __________

## 1. Put the correct drawing beside you

Open the [placement drawing](drawings/placement-R1.pdf) and [schematic](drawings/schematic-R1.pdf) from this project. The placement drawing identifies the individual component positions; the schematic identifies the electrical connections. Print the placement PDF at **100% / actual size**, not fit-to-page, if using it for a physical fit check. Its board outline should measure 95 × 79 mm. The illustration in the HTML guide is for identification and is not a scale template.

Throughout this guide, view the board **from the component side**, with “10 kHz OSCILLATOR | R1” upright along the top. The power terminal J1 is toward the lower-left; the BNC J2 projects beyond the right edge; the pot RV1 is toward the upper-right. Left/right directions below do not apply when looking at the underside.

All component bodies are fitted on this top side. Surface-mount resistors and op-amps are soldered on top. Through-hole components go through the board and are normally soldered from underneath. No SOIC-to-DIP adapters, breadboard jumpers or extra links are required.

**The four most important orientation checks:**

| Part | Correct orientation in this top view |
|---|---|
| U1, U2, U3, U4 | Package pin 1 at the upper-left of each footprint |
| D1 | Cathode stripe toward the top of the board |
| D2 | Cathode stripe toward the right of the board |
| C15 and C16 | Positive lead in the left hole; negative striped side toward the right |

These directions were checked against the actual released PCB pad coordinates and net assignments. Confirm the package markings and PCB pads as well; do not orient an IC from the direction of its printed part number alone.

## 2. Prepare the bench and tools

Keep the board completely disconnected from power, the oscilloscope and the BNC cable while soldering. Work in good light with local fume extraction and eye protection, particularly when clipping leads or using the solder pump. Wash hands after handling solder, especially if the lab uses leaded solder.

| Equipment | What you will use it for |
|---|---|
| Temperature-controlled soldering station and stand | Controlled heating; a small chisel tip around 1–2 mm is more useful than a needle tip for most of this board |
| Slightly larger compatible chisel tip | Terminal and BNC ground/mechanical joints, where more heat transfer is needed |
| Fine electronics solder wire, roughly 0.4–0.6 mm | Small controlled amounts on 0805 resistors and SOIC leads; verify the alloy on the reel |
| Brass wool or the station's approved tip cleaner | Remove oxide and old excess solder; re-tin the tip afterward |
| Fine tweezers | Place resistors and hold op-amps during the first tack joint |
| Flush cutters and small pliers | Form and trim through-hole leads without stressing component bodies |
| Holder with magnifying lens plus bench light | Hold the board and inspect each joint; clamp an empty board edge, not parts or tracks |
| CQ4LF flux pen | Apply a small amount where solder needs to wet pads and leads |
| CQNTRM-1.0 cleaner, ESD brush, lint-free wipes | Controlled cleaning and removal of dissolved residue; keep out of the pot |
| FIT0216 desoldering pump | Clear larger through-hole joints when rework is necessary |
| Fine solder wick, if available in the lab | Especially useful for small IC bridges; it was not established as part of the purchased inventory |
| ESD mat and wrist strap | Protect the op-amps during handling and soldering |
| Digital multimeter | Check values, continuity, orientation-related nets and power rails |
| Suitable dual/isolated bench supply | Supply +15 V, ground and −15 V with independently limited rail currents |
| Oscilloscope and compensated ×10 probe | Confirm startup and output without heavily loading the circuit |
| M2.5 standoffs and fasteners | Keep the finished board off conductive surfaces |

Connect the ESD equipment only through its proper grounding cords to a **verified lab ESD ground**. Have the technician identify it if uncertain; do not improvise a connection to socket contacts, pipes or an arbitrary metal surface. Keep the ICs in their antistatic packaging until needed. The mat is not the soldering iron's rest, and the wrist strap is not protection from electrical shock.

Confirm that the school provides the iron, solder, tweezers, cutters, meter, power supply, probe and fume extraction. The purchased accessories do not replace these tools. A stencil, reflow oven and hot-air gun are not needed for the assembly method below.

If this is your first surface-mount assembly, practise a few 0805 joints on a practice board before starting the oscillator. Do not use the oscillator's sensitive pads as a practice area.

## 3. Inspect the incoming PCB and dry-fit the mechanical parts

1. Check that the delivered board says R1 and matches the placement drawing. Inspect both sides under magnification for scratches across traces, loose metal, damaged pads or obstructed holes.
2. Identify the four mounting holes, the two pot mounting slots, the three terminal holes and the BNC pattern. Do not enlarge plated holes or scrape the solder mask to make a mismatched part fit.
3. Temporarily insert J1, J2 and RV1 without soldering. They must fit without bending their functional pins into a different pattern. Confirm that the BNC projects beyond the right edge and the terminal's wire-entry openings are accessible.
4. Remove these parts again so they do not obstruct the small components. Keep the pot clean and dry.
5. On the bare board, check J1 pin 1 to TP1, pin 2 to TP2 and pin 3 to TP3 for continuity. J1 is **+15 V / GND / −15 V from left to right** in the defined top view.
6. Check for an unexpected short between each pair of the three supply nets. A solid low-ohm short on the bare board needs investigation before any parts are fitted.
7. Handle the board by its edges. Do not sand the gold finish or leave fingerprints around the high-value resistor networks.

**Checkpoint:** board inspection and dry-fit PASS / FAIL: __________

## 4. Sort and identify the parts

Keep the resistors in their labeled cut-tape strips. Open one value at a time, and keep a separate container for spares. The board uses **44 fixed 0805 resistors**, not the through-hole resistor strings used on the breadboard. The required series/parallel connections are already in the PCB tracks.

An 0805 resistor is approximately 2.0 × 1.25 mm and has no polarity. Measure it before installation, preferably using a component fixture or steady probe contact; do not hold both probe contacts with your fingers when checking high values. The meter may not establish its full 0.1% tolerance, but it can catch a decade error such as 100 Ω instead of 100 kΩ. Do not rely only on tiny resistor markings.

Use the following **fitted quantities**, not the larger purchased quantities that include spares:

| Value | Fitted quantity | PCB references |
|---|---:|---|
| 47 Ω | 4 | R104, R204, R304, R404 |
| 100 Ω | 2 | R605, R805 |
| 200 Ω | 2 | R604, R804 |
| 220 Ω | 2 | R903, R1003 |
| 270 Ω | 4 | R103, R203, R303, R403 |
| 330 Ω | 4 | R102, R202, R302, R402 |
| 680 Ω | 2 | R902, R1002 |
| 1 kΩ | 8 | R12, R15, R101, R201, R301, R401, R901, R1001 |
| 2 kΩ | 1 | R11 |
| 4.7 kΩ | 2 | R603, R803 |
| 10 kΩ | 3 | R13, R503, R703 |
| 20 kΩ | 4 | R502, R602, R702, R802 |
| 47 kΩ | 1 | R14 |
| 100 kΩ | 3 | R16, R501, R701 |
| 300 kΩ | 2 | R601, R801 |

The references on the PCB differ from the logical resistor names in the original LTspice circuit. This is intentional:

| Original circuit element | PCB implementation | Nominal total |
|---|---|---:|
| R1 | R101 + R102 + R103 + R104 | 1,647 Ω |
| R2 | R201 + R202 + R203 + R204 | 1,647 Ω |
| R3 | R301 + R302 + R303 + R304 | 1,647 Ω |
| R4 | R401 + R402 + R403 + R404 | 1,647 Ω |
| RG | R13 | 10 kΩ |
| RF | R14 + R15 | 48 kΩ |
| R5 | R501 + R502 + R503 | 130 kΩ |
| R6 | R601 + R602 + R603 + R604 + R605 | 325 kΩ |
| R7 | R701 + R702 + R703 | 130 kΩ |
| R8 | R801 + R802 + R803 + R804 + R805 | 325 kΩ |
| R9 | R901 + R902 + R903 | 1.9 kΩ |
| R10 | R1001 + R1002 + R1003 | 1.9 kΩ |
| R11 equivalent | PCB R11, 2 kΩ, in parallel with R16, 100 kΩ | 1,960.78 Ω |
| R12 | PCB R12 | 1 kΩ |

**Do not put a 1.961 kΩ resistor at PCB R11:** the board achieves that equivalent with the two specified parallel resistors.

Other fitted parts:

| References | Quantity | Exact part / value | Polarity |
|---|---:|---|---|
| U1–U4 | 4 | TI OPA1656IDR, SOIC-8 | Pin 1 orientation matters |
| C1–C4 | 4 | Vishay MKP1837310011, 10 nF, 1%, polypropylene | Non-polarized |
| C5 | 1 | AVX SR215A102FARTR1, 1 nF, 1%, C0G | Non-polarized |
| C6 | 1 | Vishay MKP1837368011, 68 nF, 1%, polypropylene | Non-polarized |
| C7–C14 | 8 | KEMET C315C104K5R5TA, 100 nF X7R | Non-polarized |
| C15–C16 | 2 | Panasonic EEU-FR1H100, 10 µF, 50 V | Positive/negative matters |
| D1–D2 | 2 | onsemi 1N4148, axial DO-35 | Stripe marks cathode |
| RV1 | 1 | Alps RK09K1130A5R, 10 kΩ linear | Terminal placement matters |
| J1 | 1 | Molex 39543-0003 | Check terminal order and wire access |
| J2 | 1 | Amphenol 031-5431-10RFX | Check signal/shield pins and body orientation |

TP1–TP8 are exposed probe pads already on the PCB; there are no test-point components to install. The four mounting holes are not electrical connections.

## 5. Set up the soldering process

Use electronics solder and electronics flux. Do not use plumbing/acid flux. Confirm the solder alloy and follow the lab's process. As practical starting settings for a temperature-controlled station, use approximately **320°C for common tin/lead solder** or **350°C for common SAC lead-free solder**. These are starting settings, not universal component heat limits; a station's displayed temperature and actual tip temperature may differ.

Use the lowest setting that makes a clean joint promptly with the appropriate tip. Larger connectors may need a larger tip and better heat transfer rather than a higher temperature. Never solve poor wetting by leaving the iron on the joint indefinitely. Hakko discusses the importance of thermal recovery and tip selection in its [temperature guidance](https://kb.hakkousa.com/Knowledgebase/10297/What-are-the-different-optimal-soldering-temperatures-for-soldering-with-tinlead-solder-and-lead-free-solder).

Before starting, clean the tip and apply a thin fresh solder coating. During work, clean off excess/oxide and re-tin as necessary. Do not file a plated soldering tip. Put the iron in its stand whenever not making a joint.

For an ordinary small joint, aim to complete heating, wetting and solder addition in a few seconds. If solder will not flow promptly, remove the iron, let the part cool, and correct tip condition, flux, contact area or temperature. Component-specific limits take precedence. In particular, the Alps pot is specified for **350°C maximum tip temperature, 3 seconds maximum and one soldering application per terminal**; plan its joints carefully and do not repeatedly tack/reheat it like an ordinary connector. See the [exact Alps part specifications](https://tech.alpsalpine.com/e/products/detail/RK09K1130A5R/).

## 6. Solder all 44 resistors

Start with the accessible straight chains R101–R104, then R201–R204, R301–R304 and R401–R404. Continue with the remaining groups using the table and drawing. Work one value at a time and tick off each reference as it is fitted.

For each resistor:

1. Identify both pads and apply a small amount of flux.
2. Put a **small, low mound of solder on only one pad**. Do not pre-fill both pads with large blobs.
3. Hold the resistor with tweezers, with its body centered between the pads.
4. Reheat the tinned pad and slide the resistor's end termination into the molten solder. Keep the body flat and both ends positioned over their pads. Avoid pushing hard.
5. Remove the iron, hold still until the solder freezes, then release the tweezers.
6. Inspect the alignment before continuing. If necessary, reflow that single tack joint and realign; let it cool before more work.
7. Heat the other pad and resistor end together. Feed a small amount of solder into their junction, then remove the solder wire and finally the iron.
8. Inspect both ends. Only touch up the first end if its joint is incomplete; a sound tack joint does not need repeated reheating.

A good joint wets the pad and the metal end of the resistor, without a bridge or a raised end. A lead-free joint can be matte and still be good. The body should not stand upright, sit on a large solder mound or move when gently handled. Do not flood solder across the top of the body.

After each group, compare every fitted reference with its value in the table. Visually follow the series-chain pads and look for adjacent bridges. Take a clear photo before the larger parts obstruct the view.

Do not demand the nominal resistance from every network measured in-circuit: other resistors, capacitors and later semiconductors can create parallel paths. Use the pre-installation checks as the primary value record; an ambiguous in-circuit reading needs schematic interpretation, not an automatic component change.

**Checkpoint:** 44 resistors fitted; no extra spare parts installed; value/location review PASS / FAIL: __________

## 7. Install the four OPA1656 op-amps

Install the ICs while the nearby through-hole parts are still absent, giving the iron and tweezers clear access. This guide uses individual-pin soldering; drag soldering is unnecessary for eight pins.

All four ICs have the same top-view orientation on this board:

```text
          top of board
       pin 1        pin 8  +15 V
       pin 2        pin 7
       pin 3        pin 6
−15 V  pin 4        pin 5
```

Use the package's pin-1 index feature and the PCB's pin-1 marker. If the molding/marking is unclear, inspect it under better magnification and compare with TI's package drawing before soldering. The SOIC OPA1656 uses supply pin 8 for V+ and pin 4 for V−; do not confuse it with the single-channel OPA1655 pinout in the same [TI datasheet](https://www.ti.com/lit/ds/symlink/opa1656.pdf).

For each IC:

1. Check that it is OPA1656IDR and that all eight leads are straight and coplanar.
2. Apply a little flux to the eight pads. Lightly tin one corner pad, such as pin 1.
3. Hold the IC over the footprint with tweezers. Reheat that pad and position the package with every lead centered on its pad.
4. Remove heat, hold still, then inspect both rows from above and at a low angle. Correct alignment now, while only one pin is attached.
5. Solder the diagonally opposite corner, pin 5 if pin 1 was first. Verify that the package still sits level.
6. Solder the remaining six pins individually, using only enough solder to wet each lead and pad. Move between pins rather than keeping heat on one location.
7. Inspect all eight leads for actual wetting, bent/floating leads and bridges. Look from more than one direction; flux can hide a bridge.

A continuity beep between two adjacent pins is **not automatically a solder bridge**: some outputs and inverting inputs are intentionally connected as followers. For example, U4 pins 1–2 and 6–7 are connected by the design. Use visual inspection and the schematic to decide whether a connection is unintended. Never remove a PCB trace to eliminate an intentional connection.

If a small solder bridge forms, add a little flux and use a clean tinned tip to draw off excess solder without pushing the leads. Fine wick can help: heat wick and solder together, then lift wick and iron together while molten. Do not pull cold wick from a pad. The mechanical solder pump is better suited to through-hole joints than these small IC pads. If the IC must be removed, stop and get suitable rework help rather than prying up its leads.

**Checkpoint:** U1–U4 pin-1 orientation and all 32 lead joints PASS / FAIL: __________

## 8. Install the diodes and small capacitors

For a through-hole component, insert the part on top, hold it securely, then heat the pad and lead together from underneath. Feed solder at their junction so it wets both and flows into the plated hole. Remove the solder wire first, then the iron, and hold still until solid. Trim the excess lead afterward, leaving roughly 1 mm above the joint without cutting into the solder fillet. Catch the clipping so it cannot land on the board or fly toward your eyes.

**D1 and D2:** the dark band on each glass 1N4148 is the cathode, connected to PCB pad 1. Form the leads to the hole spacing with pliers supporting the lead near the body; do not bend hard against the glass seal. Fit horizontally with no strain. In the defined top view, **D1's band is at the upper end and D2's band at the right end**. Check twice before soldering. Avoid resting the hot iron on the glass.

**C5:** fit the 1 nF C0G part at C5, with its 5.08 mm lead spacing. It has no polarity.

**C7–C14:** fit all eight 100 nF KEMET parts, with their 2.54 mm lead spacing. These also have no polarity. Seat them close to the board at their intended standoff, without forcing the ceramic body against the PCB or leaving long flying leads. Do not relocate them; they are the local supply bypass capacitors.

Capacitor labels can be confusing: 1 nF = 1,000 pF, 10 nF = 0.01 µF, 68 nF = 0.068 µF and 100 nF = 0.1 µF. Use the labeled bag and part number as the main identification, not body color.

**Checkpoint:** both diode bands correct; C5 and all eight bypass capacitors fitted: __________

## 9. Install the film and electrolytic capacitors

Fit the four **10 nF polypropylene capacitors at C1–C4** and the **68 nF polypropylene capacitor at C6**. They are non-polarized. The lead pitch is 5 mm; let the molded body sit naturally above the board. Do not force the leads against the body, substitute a different capacitor technology, or keep heating a reluctant joint. Film capacitors deserve short soldering exposure and cooling time between attempts.

Next identify the two 10 µF / 50 V electrolytics. Their body stripe marks the **negative** lead; an untrimmed positive lead is often longer, but use the body marking as well. Each PCB pad 1 is the positive terminal.

| Capacitor | Left hole / positive lead | Right hole / negative striped side |
|---|---|---|
| C15 | +15 V | GND |
| C16 | GND | −15 V |

**C16's positive lead goes to ground.** This is correct because ground is 15 V more positive than the negative supply. Do not install C16 with its negative stripe toward ground just because C15's negative lead connects to ground. In this particular layout, both capacitors physically have their negative side facing right in the defined top view.

Before soldering, check the positive lead against the PCB plus marker and the table. After soldering, verify continuity to TP1/TP2/TP3: C15 positive → TP1, C15 negative → TP2, C16 positive → TP2, C16 negative → TP3.

**Checkpoint:** C1–C6 values and both electrolytic polarities independently rechecked: __________

## 10. Clean and inspect the accessible circuitry

Allow the board to cool before cleaning. The CQ4LF pen is a no-clean flux and its manufacturer does not require routine post-cleaning; nevertheless, remove excessive solder-wire flux, dirt and fingerprints from this precision analog board using a compatible process. Do not confuse adding flux with removing flux. See the [CQ4LF instructions](https://www.chipquik.com/datasheets/CQ4LF.pdf).

1. Follow the actual cleaner's label and safety instructions, with ventilation. CQNTRM-1.0 is the selected non-flammable flux remover; it is not a soldering flux. See its [product data](https://www.chipquik.com/datasheets/CQNTRM-1.0.pdf).
2. Use small amounts locally. Gently brush the affected area with the ESD brush without flexing small components or catching the IC leads.
3. Lift dissolved residue with a clean lint-free wipe; replace the dirty part of the wipe instead of spreading residue around.
4. Repeat locally where needed. Do not soak the complete assembly or assume every plastic component tolerates the cleaner.
5. Let the board dry completely according to the product instructions, including beneath components. Do not power a damp board and do not use the soldering iron as a dryer.
6. Reinspect for solder balls, clipped wires, bridges, lifted pads or open joints. Photograph the top and bottom.

This cleaning stage precedes pot installation deliberately. Keep cleaning liquid and flux out of RV1's mechanism during subsequent work; no full-board wash or ultrasonic cleaning is specified for this assembly.

## 11. Install the power terminal, BNC and potentiometer

**J1 power terminal:** fit the Molex part in its reviewed outline with the wire-entry side accessible. Solder one pin, verify that the housing is seated and square, then solder the remaining pins. The electrical order remains +15 V, GND, −15 V from left to right in the top view; do not infer it from the underside view. Use insulated wires suitable for the terminal, with no loose strands. Follow the terminal's wire preparation and tightening instructions; do not tin stranded wire ends merely to clamp them under a screw.

**J2 BNC:** fit the Amphenol body so the mating connector points out over the right board edge. Check fit and seating before soldering. Solder the electrical pins and the intended mounting posts so cable forces are not carried solely by the signal pin. Use adequate tip contact on the larger joints rather than pressing hard or heating indefinitely. The center contact is OUTPUT; the shield has a dedicated GND connection. Mechanical posts alone are not proof of the shield's electrical ground connection. Confirm center-to-TP8 and shield-to-TP2 with the meter after soldering.

**RV1 pot:** identify the 10 kΩ linear Alps part. Before fitting, measure across end terminals 1–3: roughly 8–12 kΩ is consistent with its ±20% tolerance. The middle electrical terminal is the wiper; resistance to either end should change smoothly as the shaft is turned. Do not force either end stop.

In the board's top view, RV1's three small electrical holes run vertically along the left of its body:

| Pot terminal | Position | Board net |
|---|---|---|
| 1 | Top small hole | VFINAL / TP7 |
| 2 | Middle small hole | OUTPUT / TP8 |
| 3 | Bottom small hole | GND / TP2 |

Fit the pot and its two metal mounting tabs into the matching holes/slots without forcing them. Hold it securely in the correct final position before applying heat. Solder all three terminals and both mounting tabs, observing the **350°C / 3 seconds / one application per terminal** manufacturer conditions. Do not repeatedly reheat it to straighten it after installation; if you cannot make a sound joint within those conditions, stop and have the lab technician help with the process.

With power disconnected, use a meter between TP8 and TP2 while turning the pot. Find the end with the lowest resistance: this is minimum output. Mark that direction for your own use; this design does not assume that clockwise necessarily increases output. At the other end TP8 connects closely to TP7. In-circuit parallel paths mean that you should not expect exactly 10 kΩ from every measurement.

Clean any remaining soldering residue locally without flooding the pot or connector interiors. Keep optional knob installation gentle; do not force a mismatched knob onto the shaft.

## 12. Mount the board and perform the unpowered inspection

Use the four M2.5 mounting positions, preferably with the purchased 10 mm standoffs. Keep washers and screw heads within the reviewed **6 mm diameter** envelope and check that no metal touches exposed copper or clipped leads. Tighten gently. Ensure the underside clears the bench; never power the PCB lying on a metal surface. Support the BNC body/board when inserting or removing a cable.

Before applying power, check every item below:

- All 44 fixed resistors fitted at the correct references, with no missing series-chain element.
- U1–U4 correctly oriented; all eight pins of each package soldered; no visible bridges.
- D1 stripe upward, D2 stripe rightward, in the defined top view.
- C15 positive to +15 V; C16 positive to GND; both negative body stripes face right.
- All eight 100 nF bypass capacitors installed; C1–C6 values correct.
- RV1 seated, all five soldered connections complete, shaft rotates smoothly.
- J1 and J2 mechanically supported and correctly seated.
- No loose lead clippings, solder balls, damp cleaner or flux pools.
- J1.1 → TP1 → every U pin 8 has continuity.
- J1.3 → TP3 → every U pin 4 has continuity.
- J1.2 → TP2 → BNC shield has continuity.
- BNC center → TP8 → RV1 pin 2 has continuity.
- No unexplained low-ohm short between +15 V and GND, −15 V and GND, or the two rails.

Capacitors can charge from the meter and semiconductor paths depend on probe polarity, so a transient beep or changing rail resistance is not automatically a fault. There is no universal resistance number that proves the assembled board good. Investigate a sustained near-zero reading and compare with the schematic before powering.

**Important output-check exception:** at minimum amplitude the pot intentionally connects the output close to ground. Therefore, a center-to-shield continuity beep at minimum can be normal. Turn the pot toward the middle before checking for an accidental output short, confirm that the resistance changes with rotation, and then return it to minimum for first power-up.

Unpowered inspection PASS / FAIL: __________  Inspector: __________

## 13. Connect the ±15 V supply correctly

Use the same suitable dual-rail lab supply arrangement as the working prototype, or ask the technician to configure a supply whose outputs are explicitly rated for series operation. A single ordinary +15 V output does not provide this board's required +15 V and −15 V rails.

For two isolated, series-capable channels, each set to 15 V, the connection is:

```text
Channel A positive ---------------- J1 +15 V
Channel A negative ----+
                       +----------- J1 GND
Channel B positive ----+
Channel B negative ---------------- J1 −15 V
```

Make these connections only with outputs disabled. Check the instrument's grounding arrangement first; do not series-connect outputs that are internally grounded or otherwise unsuitable. Do not use protective earth as a substitute for the middle circuit connection.

Before attaching the PCB, verify the supply wiring using the DMM black probe on the midpoint: red to the intended positive lead must read +15 V, and red to the intended negative lead must read −15 V. Disable the outputs again, set both voltages to zero for the controlled ramp, then connect the PCB ground first and the two rail leads. Set the current limit to **60 mA per channel** using the supply's specified method; do not short the PCB to set it.

Keep the BNC load disconnected. Set the pot to minimum. Place the board so a probe slip cannot short adjacent pins. Prefer the labeled test pads to probing the tiny IC supply leads while powered.

## 14. First power-up, with current limits

1. Enable and raise both rails together, checking at approximately ±2.5 V, ±5 V, ±10 V and finally ±15 V. At intermediate voltages you are looking for abnormal current or polarity, not demanding the final oscillator amplitude or frequency.
2. Pause briefly at each step. Monitor both channel currents and confirm that neither channel remains in current limit. If one rail fails, switch both off; do not leave the board running from only the other rail.
3. At ±15 V, measure TP1 relative to TP2 and TP3 relative to TP2. They should be approximately +15 V and −15 V respectively.
4. Expect approximately **32–45 mA per rail** with no external load, based on the four dual op-amps and the circuit estimate. This is a diagnostic expectation, not a hardware measurement already made.
5. Switch off immediately for sustained current limiting, settled current above about 50 mA on either rail, more than about 10 mA difference between rail currents, wrong rail polarity, rapid heating, odor or smoke. Do not raise the current limit to make a fault disappear.
6. If a problem occurs, disable both rails, disconnect power and check residual voltage before touching or reworking the board. Never short an electrolytic with a screwdriver. Do not solder with any supply or measurement cable connected.

The 60 mA limit reduces fault energy; it cannot make reversed ICs or reversed electrolytics safe. The unpowered checks are still essential.

Record: TP1 ______ V; TP3 ______ V; positive current ______ mA; negative current ______ mA.

## 15. Confirm oscillation and the amplitude control

Use a compensated **×10 high-impedance scope probe**, normally around 10 MΩ, with the scope channel set to match it. The intended output is high impedance; do not select a 50 Ω termination or connect a 50 Ω analyzer directly. Alps specifies an output-side resistance greater than 100 times the pot's 10 kΩ resistance, so the ×10 probe is preferable to a bare 1 MΩ scope input for this check.

Connect the probe ground only to **circuit GND / TP2**. The ground clip of an ordinary bench oscilloscope is earth-referenced; connecting it to −15 V or a signal node can short that node through the instrument. Make initial connections with the supply off if there is any chance of a slip, then repeat the controlled power-up.

| Test point | Signal / purpose |
|---|---|
| TP1 | +15 V supply |
| TP2 | Ground reference |
| TP3 | −15 V supply |
| TP4 | Gain-stage output; limiter-related distortion here is not the final output specification |
| TP5 | Buffered oscillator output — first signal point to check |
| TP6 | Filter output |
| TP7 | Fixed-divider output, before the adjustable pot |
| TP8 | Pot wiper / BNC output |

1. Start at TP5 with DC coupling and about 20 µs/div. A 10 kHz signal has a period of about 100 µs. Start with a generous vertical range, then adjust it to see the waveform clearly.
2. Verify a sustained waveform around 10 kHz. Investigate a frequency outside approximately 9.5–10.5 kHz during initial diagnosis; that broad band is not a precision frequency acceptance tolerance.
3. Inspect TP6 and TP7, then TP8. Keep probes off the sensitive RC nodes for the initial test; probe capacitance can alter oscillator behavior.
4. At minimum pot setting, very little output at TP8 is expected even while TP5 is oscillating. Turn the pot slowly toward larger output and watch the waveform.
5. Check that amplitude varies smoothly without jumps, dropouts or persistent clipping. Near full scale, approximately 4.6–5 Vpp is the model/history expectation under suitable loading, not a guarantee for the assembled PCB. Do not change the optimized resistor values merely to force exactly 5.000 Vpp.
6. Measure output DC offset at a useful nonzero amplitude, not only with the pot at ground. Investigate a settled offset magnitude above about 100 mV.
7. Examine the waveform at faster timebases and adequate bandwidth as well. A clean 10 kHz-looking trace at one slow timebase does not rule out high-frequency instability.
8. Let the board warm up for at least 10 minutes and log frequency and amplitude at 1, 5, 10 and 20 minutes under unchanged loading. Repeat startup over several power cycles; the project test plan calls for ten cold/warm cycles with every failed or delayed start recorded.

Frequency ______ Hz; full-scale amplitude ______ Vpp; DC offset ______ mV; load/probe ______; warm-up ______ min; ambient temperature ______ °C.

An ordinary scope trace proves basic function, not 75–80 dB SFDR. Use the existing [assembly-and-test procedure](assembly-and-test.md) for calibrated spectral measurements, stated bandwidth, analyzer residual checks, and matched comparison with the breadboard. Do not label predicted simulation performance as a PCB measurement.

## 16. If something does not work

| Symptom | First checks, with power removed before rework |
|---|---|
| Immediate current limit | Supply order; IC orientation; C15/C16 polarity; bridges around IC supplies and bypass capacitors |
| One rail missing | Bench wiring/current-limit state; J1 joint; continuity to the corresponding TP and IC pins |
| No signal at TP8 | Pot position first; then trace TP5 → TP6 → TP7 → TP8 |
| Signal at TP7 but none at TP8 | Pot pin joints/orientation, output short, incorrect load or cable |
| No oscillator signal at TP5 | Missing/wrong resistor in a series chain; diode direction; 10 nF values; IC joints and rail voltages |
| Frequency far from 10 kHz | 10 nF versus 100 nF mix-up; 1,647 Ω chains; solder bridge or open; excessive probe loading |
| Output badly clipped or DC-shifted | Both rails present; unintended short; filter/divider resistor placement; loading; op-amp joints |
| Operation changes when the board is flexed | Cracked/open joint or loose connector; inspect rather than continuing to flex it |
| Visible high-frequency ripple or unexpected heating | Bypass capacitor placement/joints; ground continuity; probing/cable load; IC solder faults |

For through-hole rework, add a little flux, fully melt the joint and use the pump without striking the pad. Repeat only after cooling and checking the result. A lead must move freely before removal; never pull a component against solid solder. For a difficult multi-pin connector or IC, use suitable lab rework equipment and assistance instead of lifting pads through repeated attempts.

Change one identified fault at a time, record it, inspect the repair, and repeat the relevant unpowered checks before restoring power. Do not change the oscillator topology or values as a first response to an assembly fault.

## 17. Final build record

| Check | Result / measurement |
|---|---|
| PCB revision / serial | __________ |
| Correct part inventory and mechanical fit | __________ |
| Resistor count and values | __________ |
| IC, diode and electrolytic orientation | __________ |
| Top/bottom joint inspection and cleaning | __________ |
| Unpowered continuity and short checks | __________ |
| +15 V / −15 V measured | __________ |
| Positive / negative rail current | __________ |
| TP5 oscillation and startup | __________ |
| TP8 amplitude range and offset | __________ |
| Frequency and warm-up drift | __________ |
| Ten-cycle startup test | __________ |
| SFDR / measurement conditions | Not yet measured / __________ |
| Repairs and remaining issues | __________ |

Keep the placement drawing, resistor checklist, top/bottom photographs and measurements together. Only after the first board passes basic assembly and electrical checks should you consider populating another bare PCB.

## Basis and limits of this guide

Part locations, values and orientation directions were checked against the released **R1-review-03/source/oscillator.kicad_pcb**, its BOM, and the assembly drawing. Supply limits and test expectations follow the existing project assembly-and-test procedure; no new bench results are asserted. The soldering order is adapted for clear access during hand assembly and does not change the circuit or manufacturing files. Refer to the linked manufacturer instructions for package-specific handling and process restrictions.
