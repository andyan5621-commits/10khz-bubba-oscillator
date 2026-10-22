# Circuit validation report

Date: 2026-10-22  
Scope: recovered LTspice source, exact circuit connectivity, source-to-hardware
reconciliation, and simulation evidence for the oscillator PCB baseline.

## Executive finding

The recovered literal-value schematic is a strong electrical baseline for the
measured breadboard. Its values match the user-supplied prototype list exactly,
and three independently located copies of the original final schematic are
byte-identical. A later repository copy differs only in a comment path and is
electrically identical.

The recovered filter is a **unity-gain Sallen–Key low-pass filter**, not a
multiple-feedback (MFB) filter. Both the generated netlist and the latest lab
report agree on Sallen–Key. The hardware should therefore be captured from the
recovered connectivity unless direct continuity tracing shows that the physical
prototype differs. The filter's response is centred near 10 kHz and is intended
to suppress the third harmonic near 30 kHz; “about 30 kHz” describes the spur,
not the filter's pole frequency.

The user has confirmed the archived output-potentiometer arrangement: retain
R11 and R12, connect a nominal 10 kΩ potentiometer between VFINAL and ground,
and use its wiper as the adjustable output.

## Evidence and source finality

Primary source candidate:

- `C:\Users\20252928\OneDrive - TU Eindhoven\Desktop\Oscillator works\Oscillator_Final.asc`
- 6,635 bytes, modified 2026-09-19 15:35:56 +02:00
- SHA-256 `DA4B98038B60D70400AE0741BDA58249105D45BFE32DF0B7FAD7D45102044B97`

The same bytes and timestamp occur at
`C:\PythonSolvers\Oscillator_works\Oscillator_Final.asc` and in the archived
verification run. The 2026-10-02 packaged copy has SHA-256
`617120E9475A232743465FD52DC9243DCDD9916340EE9E888FCE425C28CEFEB3`;
the sole line difference is a non-electrical comment changing an absolute Python
script path to a repository-relative path. Provenance and preserved copies are
under `reference/ltspice-recovered-2026-10-22/`.

The exact generated final netlist was produced by LTspice 26.0.2 and has SHA-256
`A91296911CCF99E2320ADA36BC12CEB669C9AE92EEA55CD0224C4C49593FAC09`.
It is the basis for the node mapping below. The later `optimized_best.net` is
corroborating evidence only: it adds a 1 MΩ || 20 pF test load, a grounded spare
follower, eight 100 nF capacitors, and two 10 µF capacitors during script
post-processing. Those additions are absent from `Oscillator_Final.asc` and must
not be mistaken for drawn-source connectivity.

The latest lab report was read directly from the Desktop copy (SHA-256
`24006EAEF735EA6FFC349B51FEFF45B06A37AF8C8693F43C9D02CEDBE775C7B4`).
Its text and embedded figure captions support ±15 V operation, the Sallen–Key
stage, seven active OPA1656 channels, decoupling, and the potentiometer wiring.
The report is narrative evidence rather than a machine-checkable wiring record;
the LTspice netlist remains the exact connectivity source, with the user's
hardware corrections taking precedence.

## Exact recovered connectivity

The OPA1656 macro-model pin order is non-inverting input, inverting input,
positive rail, negative rail, output.

| Block | Exact connections |
|---|---|
| U1 / loop amplifier | U1+ to GND; U1− = N_INV; U1 output = CORE_DRV. RG 10 kΩ from VOUT to N_INV. RF 48 kΩ from CORE_DRV to N_INV. |
| RC stage 1 / U2 | R1 1,647 Ω from CORE_DRV to RC1; C1 10 nF from RC1 to GND; U2 follower, input RC1 and output BUF1. |
| RC stage 2 / U3 | R2 1,647 Ω from BUF1 to RC2; C2 10 nF from RC2 to GND; U3 follower, input RC2 and output BUF2. |
| RC stage 3 / U4 | R3 1,647 Ω from BUF2 to RC3; C3 10 nF from RC3 to GND; U4 follower, input RC3 and output BUF3. |
| RC stage 4 | R4 1,647 Ω from BUF3 to VOUT; C4 10 nF from VOUT to GND. VOUT returns through RG to U1− and also feeds U7. |
| Positive limiter branch | R5 130 kΩ from LIM_P to CORE_DRV; R6 325 kΩ from +15V to LIM_P; D1 anode at N_INV and cathode at LIM_P. |
| Negative limiter branch | R7 130 kΩ from CORE_DRV to LIM_N; R8 325 kΩ from LIM_N to −15V; D2 anode at LIM_N and cathode at N_INV. |
| U7 isolation buffer | U7 follower, non-inverting input VOUT, output ISO. |
| U5 Sallen–Key filter | R9 1.9 kΩ from ISO to F_J; R10 1.9 kΩ from F_J to F_IN; C5 1 nF from F_IN to GND; C6 68 nF from VFILT to F_J; U5 follower, input F_IN and output VFILT. |
| U6 output buffer/divider | U6 follower, input VFILT and output BUF_OUT. R11 1,960.78431 Ω from BUF_OUT to VFINAL; R12 1 kΩ from VFINAL to GND. |
| Confirmed adjustable output | Nominal 10 kΩ pot outer terminals VFINAL and GND; wiper = ADJ_OUT. R11 and R12 remain fitted. No post-wiper buffer is evidenced. |
| Supplies | +15V and −15V relative to common GND. All seven active channels use both rails. |

The physical channel grouping stated in the report is U1/U2, U3/U4, U7/U5,
and U6 plus one unused channel across four dual OPA1656 packages. The exact PCB
package/unit designators can be reassigned without changing function. The unused
channel needs a stable termination in the PCB design; the archived appended
grounded follower is a sensible proposal, but it is not present in the final
drawn schematic and is not treated here as a recovered hardware fact.

## Value reconciliation

| Item | User-supplied hardware | Recovered final schematic | Status |
|---|---:|---:|---|
| R1–R4 | 1 kΩ + 330 Ω + 270 Ω + 47 Ω = 1,647 Ω | 1,647 Ω each | Match |
| RG / RF | 10 kΩ / 48 kΩ | 10 kΩ / 48 kΩ | Match |
| R5, R7 | 130 kΩ | 130 kΩ | Match |
| R6, R8 | 325 kΩ | 325 kΩ | Match |
| R9, R10 | 1.9 kΩ | 1.9 kΩ | Match |
| R11 | 2 kΩ || 100 kΩ = 1,960.784 Ω | 1,960.78431 Ω | Match |
| R12 | 1 kΩ | 1 kΩ | Match |
| C1–C4 | 10 nF | 10 nF | Match |
| C5 / C6 | 1 nF / 68 nF | 1 nF / 68 nF | Match |
| D1 / D2 | 1N4148 | D4148_ON model derived from 1N4148 entry | Match at part family; model-specific |
| Active channels | 7 channels in 4 × OPA1656IDR | 7 OPA1656 macro-model instances | Functional match; package mapping not encoded |
| Local / bulk bypass | 8 × 100 nF, 2 × 10 µF | Not drawn in final ASC; appended to optimization net | Hardware fact, absent from final drawn source |
| Output pot | 10 kΩ, VFINAL-to-GND, wiper output | Not drawn | User-confirmed hardware addition |

## Analytical checks

- The nominal unloaded single-section RC frequency is about 9.66 kHz for
  1,647 Ω and 10 nF. It is only an initial check because RG loads the final
  section and the active/nonlinear loop changes the exact oscillation point.
- RF/RG = 4.8 and R6/R5 = R8/R7 = 2.5, matching the recovered annotations.
- For the recovered equal-resistor Sallen–Key network, the ideal natural
  frequency is about 10.16 kHz and the ideal Q is about 4.12. This agrees with a
  resonant filter around the fundamental, with stronger rejection at H3 near
  30 kHz. It does not describe a 30 kHz MFB cutoff.
- The unloaded fixed-divider gain before the potentiometer is approximately
  0.3377. A 10 kΩ pot connected across VFINAL loads the lower leg and therefore
  changes the maximum divider ratio; the archived simulation without the pot is
  not an exact model of the confirmed output hardware.

## Archived validation evidence

The archived nominal LTspice analysis reports 9,984.35 Hz, about 4.95 Vpp at
VFINAL, and 90.783 dB harmonic-based SFDR, with H3 dominant. These are model
results for the fixed-divider output without the physical potentiometer. They
are not fresh results from this PCB project and must not be presented as PCB
performance.

The Desktop lab report records the breadboard on an external ±15 V supply. Near
full output it reports 10,052.83 Hz, Vpk 2.49 V (about 4.98 Vpp), and 88.79 dBc
fundamental-to-H3 separation over 0–100 kHz. Separate oscilloscope captures are
reported at 5.07, 3.82, and 0.800 Vpp. These measurements characterize the
breadboard plus its acquisition setup, not the future PCB.

The archived ±1% timing-component study had 46 of 256 tested corners outside
the 10 kHz ±1% frequency band. Nominal success therefore does not support a
blanket tolerance-compliance claim. The PCB should retain measurement access
and, if production compliance matters, provide a tuning or selection strategy.

## Mismatch and issue register

| Topic | Evidence | Disposition |
|---|---|---|
| Filter called “MFB about 30 kHz” in the initial brief | Exact source, generated netlist, and lab report all show unity-gain Sallen–Key around 10 kHz; 30 kHz is H3 | Open factual mismatch. Preserve recovered topology unless direct hardware tracing contradicts it. No redesign performed. |
| Pot wiring initially marked unknown | Latest report specifies VFINAL-to-GND with wiper output; user explicitly confirmed this arrangement | Resolved as hardware baseline. |
| Final ASC omits pot and decoupling | User hardware list and report include them | Add to PCB schematic; do not call the ASC a complete hardware model. |
| `optimized_best.net` contains extra scope load, spare follower, and bypass parts | Script-added content documented in archived project | Do not infer that these were all in the final drawn source. Use only where independently confirmed. |
| Spare OPA1656 channel | Four dual packages, seven active channels | PCB termination remains an engineering decision; document the chosen safe termination. |
| Rail connector, protection, and source details | Only external ±15 V and common ground are evidenced | Connector type/pin order and protection remain PCB decisions. Keep polarity explicit. |
| Output loading | Confirmed unbuffered pot wiper; archived simulation omits pot | PCB output amplitude and distortion require fresh simulation/measurement with the selected load. |
| Frequency tolerance | 46/256 archived timing corners failed ±1% | Material risk; nominal performance is insufficient evidence of tolerance-wide compliance. |

## Fresh simulation status

LTspice 26.0.2.1 is installed. Two batch invocations of an exact workspace copy
of the primary schematic returned exit code 0 but produced no netlist, log, or
raw waveform. The attempt is therefore inconclusive, and no fresh performance
numbers are claimed. No LTspice process was left running.

Before board release, a fresh simulation should model the confirmed 10 kΩ pot,
the intended external load/cable capacitance, the selected spare-channel
termination, supply decoupling, and any input/output protection actually added
to the PCB. The Sallen–Key topology should be retained for that comparison.

## Completion state

Done:

- Targeted source search, source comparison, and hash-preserved recovery.
- Exact active connectivity extraction from the LTspice-generated netlist.
- Component-value reconciliation against the user-supplied prototype.
- Lab-report extraction for supply, pot, topology, channel use, and measurement
  evidence.
- Identification of the Sallen–Key/MFB mismatch and tolerance risk.

Not done:

- No new successful transient or tolerance run.
- No claim that the archived simulation models the potentiometer or future PCB.
- No direct continuity probing of the breadboard.
- No choice of PCB rail connector, protection, spare-channel termination,
  output connector/load, or tuning strategy.

