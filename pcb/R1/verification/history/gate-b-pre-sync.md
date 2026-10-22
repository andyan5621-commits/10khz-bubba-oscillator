# Independent Gate B review — routing authorization

22 October 2026. This is the current follow-up to `independent-review.md`; that earlier report preserves the initial failure and corrected69-component history.

**Electrical schematic capture: PASS. Routing gate: awaiting final courtyard/synchronization check. Manufacturing readiness: FAIL / incomplete.**

The native schematic now contains77 components:44 fixed resistors,16 capacitors,4 dual amplifiers,2 diodes,2 connectors,1 approved Alps potentiometer and8 testpoints. All77 have footprint assignments. An independent KiCad CLI export passed `check_export.py`; the exact exported hash and detailed graph result are in `current-77part-results.json`. Seven junctions now use KiCad's generated net names because local wires replace labels; explicit aliases normalize their names, while independent pin/branch checks still verify connectivity. The prior69-part checker/export/results are preserved as `check_export_69part_baseline.py` and `accepted-69part-*`.

Testpoints independently checked:TP1+15V,TP2GND,TP3−15V,TP4GAIN_OUT,TP5N_BUF,TP6VFILTERED,TP7VFINAL,TP8OUTPUT. No probe is added to a limiter, summing or timing/filter junction. Rendered schematic was visually inspected: the functional loop, limiter, filter, divider, supply and output sections can be followed. Some net text is close to symbol pins but this does not obscure the reviewed connectivity.

## BNC drawing ambiguities resolved

The original Amphenol31-5431-10RFX revisionC drawing is retained as `drawings/amphenol-farnell.pdf`. A300dpi crop in `drawings/amphenol-hole-detail.png` resolves the compressed figure: the full mounting-post span is **10.16mm**, printed as`10,16 REF [.400]`; the thin`1` after the decimal comma can disappear at reduced rendering scale. The5.08mm half-span and0.400inch value corroborate this dimension.

Handedness is resolved independently of interpreting the standalone hole-pattern view as top or bottom. The rear elevation shows pins pointing down, with the signal contact on the connector centreline and the shell tail on the observer's left. A PCB top view with mating direction negativeY places that rear observer at positiveY, whose left is negativeX. Therefore signal(0,0),shell(−2.54,0),mounting forks(±5.08,−5.08) is the correct top-view arrangement. No physical sample is required to resolve this drawing relationship. The earlier handedness hold in `footprint-audit.md` is closed.

The two mounting forks remain unnetted mechanical pads because the outline alone does not establish their electrical continuity to shell. The separate shell contact is GND. The custom pattern's Ø0.89 contact holes and Ø2.01 fork holes match the drawing. Copper land sizes are explicit PCB engineering choices. Board/panel fit still requires review of the final placement and the intended enclosure, if any.

## Approved Alps part

The user-approved exact part is RK09K1130A5R. The [current manufacturer catalog](https://tech.alpsalpine.com/cms.media/product_catalog_rv_02_rk09k_rk09d_en_26d4cb95ac.pdf), update2510, associates it with Drawing3: single10kΩ linear1B section, vertical knob,20mm shaft-length datum. The original and inspected rendering are `drawings/alps-rk09k.pdf` and `drawings/alps-drawing3.png`.

The installed KiCad `Potentiometer_THT:Potentiometer_Alps_RK09K_Single_Vertical` matches nominal electrical contact pitch2.5mm, threeØ1mm holes, and the tab-centre geometry. Rotating the mounting-side manufacturer's view90° gives KiCad pins1/2/3 at(0,0),(0,2.5),(0,5) and mounting tabs at(7,−1.9),(7,6.9). The drawing's10.6mm outside tab-hole span minus1.8mm hole width gives8.8mm centre spacing. These are mechanical tabs, not extra electrical terminals. The specified circuit identifies pin2 as wiper.

One fabrication detail remains for the drill review: KiCad uses oval2.1×1.8mm plated slots while the manufacturer's drawing represents rectangular openings with those overall dimensions and no corner-radius detail. The contact numbering, centre locations and routing envelope are accepted; final tab fit should not be described as an exact slot-shape match without addressing the rounded ends. This is a fabrication fit item rather than an electrical routing prohibition.

## Molex conservative body reservation

The exact primary drawing confirms threeØ1.20mm holes at5mm pitch,15mm body width and9.5mm body depth. The independent pass has not yet visually substantiated the proposed4.75mm row-to-body-edge datum. Do not convert the centered drawing into a verified fact.

As authorized by the chief, a conservative courtyard can contain the full9.5mm possible body depth on both sides of the pin row, with additional dimensional tolerance/assembly margin. This removes reliance on the unknown centering for collision clearance. The connector is a straight through-hole part with the row within its body projection. With pin1 atx=0, the nominal width endpoints are−2.5 and12.5mm; width tolerance and margin must also be included. Once this larger envelope is present and checked against neighboring components/board edge, the uncertain centered body sketch does not block routing. The final report must retain its approximate status. No blanket physical-sample requirement is imposed.

## Fresh simulation evidence reviewed

Read actual `reports/runtime-check/baseline.net`, `hardware_full.net`, `hardware_startup.net`, corresponding LTspice logs and analysis JSON. These runs now have completed logs and raw waveform files; the earlier no-artifact batch attempt is superseded.

- Baseline log:9984.351726Hz,4.952939705Vpp.
- Confirmed10kΩ pot at full output with1MΩ||20pF test load:9984.351726Hz,4.642418832Vpp.
- No kick source, LTspice supply-startup ramp:9984.351681Hz,4.642418698Vpp in the late window.

The full-pot deck represents the end-stop case by a10kΩ shunt, correctly retaining the1kΩ lower divider. The startup deck removesIKICK and uses the transient`startup` option. The reported harmonic analysis reproduces approximately90.783dB for the baseline. This supports nominal circuit continuity and one modeled startup condition, not hardware SFDR, all loads, all pot positions, or component-tolerance compliance. Detailed report: `simulation/fresh-validation-2026-10-22.md`.

## Board synchronization and subsequent gates

`check_board_parity.py` independently compares the native PCB pad nets and footprint identities against the current exported schematic. It does not import the layout generator and does not substitute pad assignment for copper connectivity. An early rerun correctly rejected the69-footprint board against the77-component schematic because the8 testpoints and rewritten net assignments had not yet been synchronized. A new result is required after the layout update.

Routing may begin only after the final Gate B disposition is recorded. Gate C/D fabrication checks still require actual tracks, plane fill, full DRC, schematic parity, placement/return-path review and mechanical/drill review. No fabrication release or order is authorized by this report.
