# Revision and release status

- Reference R0: accepted; recovered original final source and confirmed physical additions preserved.
- Schematic R1: 77 components, 44 fixed resistors, 51 nets. ERC 0 violations; independent graph PASS.
- PCB R1: 95 × 79 mm, 81 footprints including four mechanical holes, 591 segments, 39 vias, continuous bottom ground.
- Final native DRC: 0 violations, 0 unconnected, 0 schematic-parity issues.
- Gate A/B/C: PASS. Gate D independent engineering package: PASS; no known unresolved critical electrical/manufacturing issue.
- Overall prototype readiness: CONDITIONAL PASS pending ordinary incoming-fit checks, actual assembly/bench validation and user release.
- Final immutable candidate: fabrication/review-packages/R1-review-03. Earlier review-01/02 are superseded and must not be ordered.
- Board SHA256: a4f358f10eaf822501065362decd702d36b8ac9826cc2c7e55d44460478eb4e2.
- Schematic SHA256: cc4e9bd008f168a4e64262c612c48e86a04cea780c80a114a0fdfe0a20036169.
- Exports: seven Gerber X2 layers, separate plated/non-plated Excellon; independent visual and coordinate inspection PASS.
- Simulations: four nominal transients and four bounded parasitic derivatives accepted. One 5 pF limiter attempt timed out and is rejected. These are not physical measurements.
- Gate E: user fabrication release pending. Purchases: none authorized or placed. Files uploaded: none.
- Physical PCB assembly/tests: not performed. ≥75 dBc measured acceptance remains to be demonstrated.
