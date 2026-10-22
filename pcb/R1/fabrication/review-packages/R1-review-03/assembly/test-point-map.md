# Test-point map — schematic revision with TP1–TP8

These are exposed PCB probe pads; no separately purchased test-pin parts are required. Confirm the released board revision and connector polarity before applying power. Coordinates below are from the native 95 × 79 mm R1 layout, viewed from the component side: X increases right from the left board edge, Y increases down from the top edge. The KiCad absolute outline origin is (50,47) mm.

| Pad | Net / purpose | Measurement |
|---|---|---|
| TP1 | +15V | Positive rail relative to TP2 |
| TP2 | GND | Common measurement reference; short probe ground connection |
| TP3 | -15V | Negative rail relative to TP2; do not short it to an earth-ground probe clip |
| TP4 | GAIN_OUT | Oscillator loop-amplifier output; nonlinear stabilization may be visible here |
| TP5 | N_BUF | Buffered copy of the core output, before the filter; preferred frequency/startup probe location |
| TP6 | VFILTERED | Sallen–Key output, before the output buffer/divider |
| TP7 | VFINAL | Fixed-divider junction / potentiometer high end |
| TP8 | OUTPUT | Pot wiper / BNC centre signal; final amplitude and spectral measurement |

| Pad | X from left edge (mm) | Y from top edge (mm) |
|---|---:|---:|
| TP1 | 25.0 | 67.0 |
| TP2 | 31.0 | 67.0 |
| TP3 | 37.0 | 67.0 |
| TP4 | 20.0 | 40.0 |
| TP5 | 51.0 | 38.0 |
| TP6 | 59.0 | 47.2 |
| TP7 | 72.0 | 57.0 |
| TP8 | 77.0 | 52.0 |

`component-placement.csv` contains all 77 electrical components/probe pads and four mechanical holes, with both relative and KiCad coordinates. It is an assembly reference, not an approved pick-and-place machine file.

The test pads avoid additional connections at the limiter junctions, inverting summing input, timing-capacitor nodes and filter's sensitive RC junction. Prefer a high-impedance low-capacitance probe for internal checks and document its input capacitance. Do not infer waveform quality at TP4 from the filtered-output target.

BNC shell is common ground. The connector's 50 Ω construction does not mean the circuit should drive a 50 Ω termination. The unbuffered potentiometer output is load dependent; use the documented high-impedance measurement configuration and reproduce it for prototype-versus-PCB comparison.

Final output measurements are at TP8/BNC, not TP7, unless the potentiometer is at its verified maximum setting. Scope and spectrum measurements taken at different amplitudes or with different loads must not be combined into a single performance claim.
