# Engineering decision log

| ID | Date | Decision | Basis / status |
|---|---|---|---|
| D001 | 2026-10-22 | Preserve physical prototype topology and effective component values | Explicit user instruction; do not treat prior simulation as physical measurement |
| D002 | 2026-10-22 | Use four OPA1656IDR dual amplifiers as user-specified stock baseline | Pin use/topology and package fit still need source/datasheet checks |
| D003 | 2026-10-22 | Treat output pot as an unresolved circuit change | User requests adjustability; no pot topology, range, or load evidence yet |
| D004 | 2026-10-22 | Default fabrication proposal: two-layer FR-4, 1.6 mm, 1 oz | User specification; actual manufacturer design rules require verification |
| D005 | 2026-10-22 | Run three specialists concurrently and rotate remaining roles | Tool concurrency limit of four total; exact GPT-5.6 unavailable so use GPT-5.6 Sol |
| D006 | 2026-10-22 | No manufacturing release before A–D and explicit user release/purchase approval | User quality gates and transaction restriction |
| D007 | 2026-10-22 | Preserve recovered Sallen–Key filter connections | Initial MFB description conflicts with original circuit; original circuit controls |
| D008 | 2026-10-22 | Retain R11/R12 and add 10 kΩ pot across Vfinal/GND, wiper output | Archive plus explicit user confirmation in this chat; suitable TinyTronics PCB pot may be selected |
| D009 | 2026-10-22 | Preserve all 44 physical resistor elements from the user table | Avoid silent consolidation; exact nominal networks now independently graph checked |
| D010 | 2026-10-22 | Terminate unused OPA1656 channel as unity follower with grounded non-inverting input | Uses eighth channel without altering signal path; included in corrected schematic and derivative simulation |
| D011 | 2026-10-22 | Add small probe pads on supplies, ground and buffered signal nodes | User requested test access; avoid extra pads on RC/filter summing/limiter nodes. Mapping to be checked independently |
| D012 | 2026-10-22 | Select Alps Alpine RK09K1130A5R 10 kΩ linear PCB potentiometer | Exact documented alternative explicitly approved by user; TinyTronics live site unavailable. Purchase remains unauthorized |
| D013 | 2026-10-22 | Gate A reference baseline accepted for schematic implementation | Original source hashes/graph, user values, confirmed hardware additions, archived rails and fresh nominal transients agree sufficiently to preserve baseline. Recorded tolerance/load/model limits remain open validation risks |
| D014 | 2026-10-22 | Reserve Molex body full 9.5 mm depth on both sides of pin row plus margin | Exact holes/pitch verified; centered body offset remains unverified. Conservative actual courtyard clears adjacent parts and board edge, independently checked |
| D015 | 2026-10-22 | Gate B approved; authorize final two-layer routing | Independent current-board parity: 77 components, 172 electrical pads; ERC 0/0; placement geometry DRC 0; J1 envelope minimum 1 mm edge margin. This is not a routed-board or fabrication approval |
| D016 | 2026-10-22 | Preserve pot pin mapping; verify knob direction during assembly | Manufacturer drawing confirms pin 2 wiper but inspected sources do not explicitly identify the electrical CW endpoint. No directional silk claim; topology unchanged |
| D017 | 2026-10-22 | Accept R1 layout after independent review and remove redundant VOUT loop | Four duplicate-path segments removed, shortening VOUT by 7.407 mm to 83.772 mm. Remaining detour avoids extra RC crossings and bottom-plane disruption; no long output/gain aggressor adjacency found. Bounded shunt-capacitance results do not establish extracted coupling or physical performance |
| D018 | 2026-10-22 | Reconcile bare test-pad BOM flags and local silk-only footprint variants | Unified native schematic parity caught TP1–8 metadata differences; corrected schematic in_bom flags with unchanged nets. C7/U3 local variants preserve all pad geometry while clearing exposed vias |
| D019 | 2026-10-22 | Freeze R1-review-03 as the only current engineering candidate | Actual R1 silk, ENIG/R1 stackup/job metadata; independent ERC/DRC/parity and coordinate-by-coordinate Gerber/drill audit pass. Review-01/02 superseded |
| D020 | 2026-10-22 | Chief accepts Gates C/D and presents package for user fabrication approval | Independent engineering package PASS, no known unresolved critical electrical/manufacturing issue. Normal incoming fit, actual hardware validation and user release remain conditions; no purchase authorized |
