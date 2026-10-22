# Engineering risk register

Updated 22 October 2026 after Gate B approval. Closed items remain visible for traceability.

| ID | Severity / state | Risk | Evidence / remaining closure |
|---|---|---|---|
| R001 | CLOSED for implementation | Simulated source differs from successful physical circuit | Original final ASC recovered and hashed; physical resistor chains, pot and bypass additions reconciled. Future hardware comparison still required |
| R002 | CLOSED | Supply rails unknown | Archived physical design establishes ±15 V; captured power pins independently verified |
| R003 | CLOSED for engineering release; incoming checks remain | Reserved part footprint mismatch | Exact stock MPNs/drawings checked; BNC handedness and conservative Molex envelope accepted. Final actual drilled/slot coordinates match native geometry; exact-model Alps standard footprint accepted with ordinary incoming fit check |
| R004 | MEDIUM / OPEN | Pot load and direction affect use | Exact Alps approved; 10 kΩ across retained divider, wiper output. High-impedance load required; check knob direction on assembly without promising CW increase |
| R005 | MEDIUM / RESIDUAL HARDWARE RISK | Limiter/filter/timing nodes sensitive to capacitance/leakage/coupling | Actual routing/return review passed; redundant VOUT loop removed. Four bounded capacitance cases settled. No field extraction or trace-coupling simulation; confirm performance on assembled hardware |
| R006 | HIGH / CONTROLLED | Simulated SFDR mistaken for measured performance | Evidence classes separated. Qualified ≥75 dBc hardware acceptance and ≥80 dBc objective require actual matched-load measurement and documented system residual |
| R007 | HIGH / OPEN | Oct 24–25 weekend release threatens Oct 31 delivery | European expedited services researched; live dated quote and user order approval still required; no delivery guarantee |
| R008 | CLOSED for selection; procurement open | Resistor values/technology undefined | Exact 44-element implementation retained. Fifteen selected 0805 thin-film 0.1%/25 ppm values, 74 planned pieces including spares. No purchase made |
| R009 | RELEASE CONTROL ACTIVE | Wrong revision or unapproved purchase | Gates A–D pass for R1-review-03 only. Earlier candidates superseded; hashes and immutable package identify correct files. User fabrication approval and purchase approval remain mandatory |
| R010 | MEDIUM / OPEN | Full-scale amplitude differs between nominal model and archived prototype | Model with confirmed pot predicts 4.642 Vpp; archived prototype approximately 4.98 Vpp. Preserve values and compare under equivalent measurement conditions; no guaranteed 5 Vpp |
| R011 | MEDIUM / OPEN | Frequency tolerance/startup across corners not established | Nominal supply-ramp startup passes; archived 46/256 timing corners exceeded ±1%. No universal frequency-tolerance or startup guarantee |
| R012 | MEDIUM / OPEN | No enclosure definition | Standalone board with mounting/access envelope; any later enclosure must be checked against connector projection, shaft height and tool access before fabrication of that enclosure |
