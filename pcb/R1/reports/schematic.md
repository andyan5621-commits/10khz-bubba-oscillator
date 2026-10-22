# Schematic capture report

Status: **native KiCad schematic captured and electrically verified; not released for fabrication or routing**.

## Authoritative files

- `schematic/oscillator.kicad_sch` — authoritative, self-contained KiCad 9 schematic.
- `schematic/oscillator.kicad_pro` — KiCad project file.
- `schematic/Oscillator.kicad_sym` and `schematic/sym-lib-table` — project-local symbol library used by ERC.
- `schematic/fp-lib-table` — project-local reference to the shared custom footprint library in `pcb/Oscillator.pretty`.
- `schematic/oscillator.net` — KiCad CLI netlist exported from the native schematic.
- `schematic/erc.rpt` — KiCad CLI ERC result.
- `schematic/generate_schematic.py` — deterministic source generator.
- `schematic/oscillator.sch` and `schematic/oscillator-cache.lib` — compatibility/reference output only; not authoritative.
- `reports/schematic-preview/oscillator.pdf` and `oscillator.png` — current rendered drawing used for visual review.
- `schematic/history/` — retained rejected netlist/ERC outputs; these are not canonical inputs.

## Facts captured

- Source circuit: `C:\Users\20252928\Documents\Codex\projects\10khz-bubba-oscillator\simulation\ltspice\optimized_best.net`, corroborated by `Oscillator_Final.asc`.
- Supply is external `+15 V / GND / -15 V` through J1.
- Four OPA1656IDR dual amplifiers provide seven active channels and one terminated spare channel.
- OPA1656IDR SOIC-8 pinout was checked against the TI OPA165x Rev. C data sheet: pin 1 OUT A, 2 -IN A, 3 +IN A, 4 V-, 5 +IN B, 6 -IN B, 7 OUT B, 8 V+. The assigned footprint is `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm`.
- The oscillator is the recovered four-stage Bubba network. The nonlinear limiter and both diode polarities match the LTspice node order.
- The post-oscillator filter is the recovered unity-gain Sallen-Key topology: input follower, R9/R10 network, C5 to ground, C6 feedback, and filter follower.
- R11 remains `2 kOhm || 100 kOhm`, R12 remains `1 kOhm`, and RV1 is `10 kOhm` from VFINAL to ground. RV1 wiper drives the BNC center contact.
- J1 pin mapping is pin 1 `+15V`, pin 2 `GND`, pin 3 `-15V`.
- J2 pin mapping is pin 1 `OUTPUT` (BNC center), pin 2 `GND` (shield).
- The eight `100 nF` local bypass capacitors and two `10 uF / 50 V` bulk capacitors are included.
- TP1-TP8 provide the requested 1.5 mm circular probe pads on `+15V`, `GND`, `-15V`, `GAIN_OUT`, `N_BUF`, `VFILTERED`, `VFINAL`, and `OUTPUT`, respectively. No extra pads were added to RC, limiter, or filter junctions.
- RV1 is the user-approved Alps Alpine `RK09K1130A5R`, 10 kOhm linear, using `Potentiometer_THT:Potentiometer_Alps_RK09K_Single_Vertical`.

## Physical resistor implementation

The schematic contains **44 fixed resistor bodies** plus RV1. Functional values are preserved as the user's prototype series/parallel networks:

| Functional element | Physical references | Build | Effective value |
|---|---|---|---:|
| R1 | R101-R104 | 1k + 330 + 270 + 47 | 1647 ohm |
| R2 | R201-R204 | 1k + 330 + 270 + 47 | 1647 ohm |
| R3 | R301-R304 | 1k + 330 + 270 + 47 | 1647 ohm |
| R4 | R401-R404 | 1k + 330 + 270 + 47 | 1647 ohm |
| RG | R13 | 10k | 10k |
| RF | R14, R15 | 47k + 1k | 48k |
| R5 | R501-R503 | 100k + 20k + 10k | 130k |
| R6 | R601-R605 | 300k + 20k + 4.7k + 200 + 100 | 325k |
| R7 | R701-R703 | 100k + 20k + 10k | 130k |
| R8 | R801-R805 | 300k + 20k + 4.7k + 200 + 100 | 325k |
| R9 | R901-R903 | 1k + 680 + 220 | 1.9k |
| R10 | R1001-R1003 | 1k + 680 + 220 | 1.9k |
| R11 | R11, R16 | 2k || 100k | 1960.784 ohm |
| R12 | R12 | 1k | 1k |

## Stock facts recorded in symbol fields

- C1-C4: Vishay `MKP1837310011`, 10 nF, 1%, polypropylene, 5 mm pitch stock part.
- C5: KYOCERA AVX `SR215A102FARTR1`, 1 nF, 1%, C0G/NP0, 5.08 mm radial pitch stock part.
- C6: Vishay `MKP1837368011`, 68 nF, 1%, polypropylene, 5 mm pitch stock part.
- C7-C14: KEMET `C315C104K5R5TA`, 100 nF radial stock part.
- C15-C16: Panasonic `EEU-FR1H100`, 10 uF / 50 V radial stock part.
- D1-D2: onsemi `1N4148`, DO-35.
- J1: Molex `39543-0003`.
- J2: Amphenol `031-5431-10RFX`.
- RV1: Alps Alpine `RK09K1130A5R`, 10 kOhm linear.

## Verification done

- KiCad 9.0.6 parsed the native schematic and exported `oscillator.net` with exit code 0.
- Export contains 77 BOM components: the prior 69-part circuit plus exactly eight one-pin test points. It still contains 44 fixed resistors, four dual op-amp packages, 16 capacitors, two diodes, RV1, and two connectors.
- Export contains 51 named nets and all 32 OPA1656 package pins.
- KiCad ERC completed with **0 errors and 0 warnings**. The registry-access messages printed by the sandbox do not affect the CLI return or generated report.
- Independent comparison of the final 77-part export passed with no failures. It confirmed 77 components, 44 fixed resistors, 51 nets, the complete 32-pin op-amp mapping, component polarities, all eight requested test-point mappings, every footprint assignment, and the exact approved Alps potentiometer MPN. Evidence is retained in `verification/current-77part-results.json` and `verification/independent-77part-export.net`.
- Visual review of the new rendering confirmed visible follower feedback loops, wired series chains, a wired Sallen-Key network, separated value/reference fields, a dedicated power block, and readable test-access/output sections.

## Assumptions and implementation decisions

- Package assignment is U1: oscillator gain/follower 1; U2: oscillator followers 2/3; U3: filter input/filter follower; U4: output follower/spare. This is an implementation allocation across identical dual channels; it does not change the recovered circuit graph.
- The spare U4B is explicitly terminated as a grounded unity follower. The source LTspice drawing did not show that channel, while the archived optimization netlist did. This is retained as the safe hardware implementation baseline.
- J1 pins are marked as power outputs in the project-local symbol solely so ERC recognizes the external connector as the rail source.

## Assigned footprints pending physical review

- The 44 fixed resistors use `Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder`.
- D1/D2 use `Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal`.
- C1-C16 use the exact project custom/standard mappings in `pcb/footprint-manifest.csv`.
- J1/J2 use the drawing-derived project footprints. Both still require the fit/handedness checks recorded in the layout report.
- TP1-TP8 use `TestPoint:TestPoint_Pad_D1.5mm`.
- Keep each IC's two 100 nF bypass capacitors adjacent to pins 8 and 4, with the shortest practical return to ground.

## Open items

- Complete physical 1:1 fit review for the drawing-derived Molex and Amphenol footprints and confirm BNC handedness/post continuity.
- Complete physical fit review for the selected Alps potentiometer and the assigned passive footprints.
- Reconcile the BNC board-edge/mechanical keepout and enclosure constraints before placement release.

## Not done

- No PCB tracks, planes, final placement, Gerbers, fabrication drawings, or assembly release were produced here.
- This capture is not an approved fabrication baseline until physical footprint reconciliation and the project approval gates are complete.
