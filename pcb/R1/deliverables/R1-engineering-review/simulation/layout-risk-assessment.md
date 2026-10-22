# Layout parasitic risk assessment

Date: 2026-10-22  
Scope: bounded shunt-capacitance sensitivity of the actual oscillator PCB
program and review of the present routing candidate. No PCB parasitic extraction
or hardware performance claim is made.

## Decision

Retain the substantially continuous bottom GND plane. The completed shunt-
capacitance cases do not justify local plane exclusions under N_INV, the limiter
threshold nodes, the filter nodes or the oscillator RC nodes. A void would also
remove shielding and can lengthen return paths. Reduce sensitive-net copper
length, area, vias, stubs and adjacency to aggressors before considering any
localized plane change.

The main observed sensitivities are filter amplitude and oscillator frequency.
The present routing candidate therefore needs another analog-routing pass,
especially for the long VOUT/final-RC connection and the first RC node. The
limiter threshold nodes remain a coupling/layout priority even though the
accepted 1 pF shunt case caused only a small nominal-model change.

## Facts

The reference is the already completed nominal `hardware_full` transient:
9984.351724 Hz, 4.642418862 Vpp, 90.783344 dB model SFDR and settled at 50 ms.
It includes the confirmed 10 kOhm full-scale pot load, 1 MOhm || 20 pF
measurement load, bypass capacitors and terminated spare channel. The nominal
case was not rerun for this work.

Four derivative decks reached 50 ms and passed the existing coherent 20-cycle
late-window settling check:

| Added lumped shunt assumption | Frequency change | Vpp change | Model SFDR change | Finding |
|---|---:|---:|---:|---|
| 5 pF at N_INV | +0.0000485 Hz (+0.000000485%) | +0.0607 mV (+0.00131%) | -0.000622 dB | Negligible response at this bound. |
| 1 pF each at LIM_P and LIM_N | +0.186634 Hz (+0.001869%) | -1.938 mV (-0.04175%) | +0.018379 dB | Small but more responsive than N_INV; keep both branches compact and symmetric. |
| 5 pF each at F_J and F_IN | -0.00000136 Hz | -23.070 mV (-0.49695%) | +0.006561 dB | Largest amplitude response; compact Sallen-Key junction layout matters. |
| 5 pF each at RC1, RC2, RC3 and VOUT | -4.963607 Hz (-0.049714%) | -0.269 mV (-0.00580%) | -0.009331 dB | Largest frequency response; added RC-node capacitance consumes frequency margin. |

The model SFDR changes are small and some are positive. A positive model delta
must not be read as a layout improvement: these cases contain only ideal shunt
capacitance and omit coupled interference, leakage and PCB loss.

The actual `pcb/routing-candidate.kicad_pcb` contains a continuous bottom GND
zone apart from mechanical clearances. Inspection of its routed copper gives
the following total track lengths; these are geometry facts and are not
converted to capacitance:

| Functional node | PCB net | Total track length | Vias |
|---|---|---:|---:|
| N_INV | `/N_INV` | 24.229 mm | 0 |
| Positive limiter threshold | `Net-(D1-K)` | 7.236 mm | 0 |
| Negative limiter threshold | `Net-(D2-A)` | 6.781 mm | 0 |
| RC1 | `Net-(U1B-+)` | 32.326 mm | 2 |
| RC2 | `Net-(U2A-+)` | 17.707 mm | 0 |
| RC3 | `Net-(U2B-+)` | 13.230 mm | 0 |
| VOUT / final RC node | `/VOUT` | 91.179 mm | 0 |
| F_J | `Net-(C6-Pad2)` | 9.364 mm | 0 |
| F_IN | `Net-(U3B-+)` | 10.134 mm | 0 |
| VFILTERED | `/VFILTERED` | 24.452 mm | 2 |

The intermediate routing log recorded an initially failed direct ground escape
for U1 pin 3. That finding is stale: the later board revision corrected the
connection. Native KiCad 9.0.6 DRC records dated 02:44:28 for
`routing-candidate.kicad_pcb` and 02:44:34 for `oscillator.kicad_pcb` both report
zero violations and zero unconnected items. The route lengths above were read
from that later routing candidate.

## Assumptions

- The added 1 pF and 5 pF values are deliberate screening bounds. They are not
  measured, field-solved or calculated from route length.
- Capacitance is represented from the named node to ideal GND. Mutual coupling,
  distributed effects and via inductance are absent.
- The OPA1656 and 1N4148 models, supplies, temperature, circuit values and
  nominal output load are unchanged from `hardware_full`.
- The filter case adds 5 pF to both internal nodes together; the RC case adds
  5 pF to all four timing nodes together. These cases identify block-level
  sensitivity, not individual-node attribution or linear scaling.

## Routing constraints from this assessment

1. Keep the bottom GND plane continuous through the analog area. Do not add a
   local N_INV/limiter/filter/RC plane void based only on these results.
2. Rework VOUT so the C4, R4-chain end, U3 input and R13 return connection form
   the shortest practical local tree. Do not let this final timing node follow
   the connector or post-filter output route. The present 91.179 mm total is a
   layout risk because VOUT is one of the four timing nodes.
3. Shorten RC1 and remove its two vias if practical. Keep RC1-RC3 top-layer,
   direct and free of testpoint stubs. Preserve the existing decision not to put
   test pads on the RC junctions.
4. Keep F_J and F_IN within the U3/R9/R10/C5/C6 cluster. Preserve the short
   no-via internal-node routes, keep the C6 feedback path compact, and separate
   these nodes from VFINAL/OUTPUT, supply-entry routes and fast op-amp outputs.
5. Keep LIM_P and LIM_N copper small and geometrically similar. Minimize copper
   on the intermediate nodes of the physical 130 kOhm and 325 kOhm resistor
   chains, avoid long parallel runs, and keep driven/supply/output routes away.
6. Keep N_INV local to U1, D1/D2, R13 and R14. Its small shunt sensitivity does
   not remove the risk of coupled interference, which this study did not model.
7. Preserve the corrected U1.3 GND connection and retain short ground
   connections for local bypass capacitors and filter/timing capacitor returns.
   Review return continuity after any reroute and refill the plane before DRC.

A localized plane exclusion should be reconsidered only if routed-board
extraction or field analysis shows materially larger node-to-plane capacitance
than the screening assumptions and a return-path/coupling review demonstrates
that the exclusion improves the full layout. No such evidence exists now.

## Modifications made for this assessment

- Copied the nominal `hardware_full` netlist and its two local model libraries
  into `simulation/parasitics/`; the copies preserve the baseline values.
- Added one derivative-only group of ideal shunt capacitors per accepted deck.
- Added a reproducible hidden-window LTspice runner and machine-readable JSON
  analyses under `simulation/parasitics/`.
- No schematic, PCB, nominal simulation, component value or topology was
  modified.

## Open issues and limitations

- A symmetric 5 pF limiter case found the operating point but exceeded the
  300 s runtime guard. Its partial waveform was rejected. The completed 1 pF
  limiter case does not prove behavior at 5 pF.
- No individual F_J/F_IN or RC1/RC2/RC3/VOUT separation was run; the four-run
  bound was used to keep the study limited.
- No trace-to-trace or rail-to-sensitive-node coupling case was run. These may
  matter more than shunt capacitance when routes run in parallel.
- No routed-board parasitic extraction, field solve, impedance model,
  tolerance/temperature sweep or hardware measurement was performed.
- The existing component-tolerance frequency risk remains separate and larger
  than the nominal derivative changes assessed here.

## Completion state

Completed: actual-netlist review; local working-directory/model verification;
four accepted derivative transients; completion, endpoint and settling checks;
comparison with the unchanged nominal result; routing-candidate geometry review;
and a plane/route-risk decision.

Not executed: nominal rerun, topology optimization, board edits, ground-plane
cutouts, parasitic extraction, field analysis, extra sensitivity sweeps, hardware
assembly or measurement.

