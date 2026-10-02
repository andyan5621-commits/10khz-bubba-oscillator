# Design and component values

The final oscillator uses four 1,647 Ω / 10 nF timing sections. The inverting
gain magnitude is RF/RG = 48 kΩ / 10 kΩ = 4.8; RG loads the last RC section,
so the ideal unloaded 1/(2πRC) relation is only an initial approximation.
The symmetric 1N4148 limiter uses R5 = R7 = 130 kΩ and R6 = R8 = 325 kΩ.

The output chain is U7 isolation buffer → U5 Sallen–Key filter → U6 output
buffer → fixed divider. The filter uses R9 = R10 = 1.9 kΩ, C5 = 1 nF, C6 = 68 nF;
its ideal Q is approximately 4.123. In optimization records, the separate
parameter called `Q = 2.5` is the **limiter resistor ratio**, not filter Q.

R11 = 2 kΩ || 100 kΩ = 1,960.784 Ω; R12 = 1 kΩ. Both remain installed in the
breadboard. The 10 kΩ potentiometer connects from their Vfinal junction to ground,
and its wiper is the measured adjustable output. It is not included in the
optimization simulations. Its loading and the lack of a post-wiper buffer
make delivered amplitude load-dependent.

Four dual OPA1656 packages supply seven active signal-path channels. The hardware
uses external ±15 V rails, eight local 100 nF bypass capacitors (one per rail per
module), and two 10 µF bulk capacitors. One faulty amplifier channel was excluded;
the functioning channel in that module provided U6.

See [resistor-bom.csv](resistor-bom.csv) for the physical resistor combinations
and the [report](report/Oscillator_lab_report_performance_complete.docx) for the
derivations and full component table. The equivalent values in the LTspice
schematic represent these combinations, not individual purchased resistors.

## Recorded design progression

1. Initial RC/gain hand calculations, followed by diode amplitude limiting.
2. Simulation correction of amplitude and frequency: 54.64 dB SFDR.
3. Local optimization of the unfiltered core: 58.252 dB, with H3 dominant.
4. Q ≈ 4.05 filter design: predicted H3 separation improvement of 30.01 dB;
   filtered simulation produced 88.47 dB.
5. Real device models and discrete resistor optimization: 90.783 dB SFDR.
6. Individual tolerance checks, then combinational timing and gain checks.
7. Breadboard build, module checks, and recorded waveform/spectral measurements.

OPA1656 and 1N4148 library models were introduced at the real-component mapping
stage. The earlier 54.64, 58.252, and 88.47 dB stages used generic models.
