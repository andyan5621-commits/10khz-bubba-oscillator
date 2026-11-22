# R1 assembled PCB — hardware measurement record

## User-reported results recorded 19 November 2026

Source: direct user annotations in the project conversation. These are hardware readings reported by the user, not simulation results or measurements independently performed by the assistant. Actual acquisition time, warm-up duration, board serial number and full instrument settings were not supplied with this entry. Displayed digits do not establish calibrated measurement accuracy.

| Quantity | Reported result | Qualification |
|---|---|---|
| Positive rail, TP1 relative to TP2 | +15.0146 V DC | User-supplied multimeter reading; instrument model and range not specified for this entry |
| Negative rail, TP3 relative to TP2 | -15.0292 V DC | User-supplied multimeter reading; instrument model and range not specified for this entry |
| Positive rail current, Delta Output 2 in the agreed wiring | 0.03 A, approximately 30 mA | Supply display reading only; no additional precision claimed |
| Negative rail current, Delta Output 1 in the agreed wiring | 0.03 A, approximately 30 mA | Supply display reading only; no additional precision claimed |
| Output frequency | 10.005 kHz = 10,005 Hz | Keysight DSO-X 3014T oscilloscope reading |
| Maximum output amplitude | 4.58 Vpp | Reported in response to maximum-output measurement request; warm-up duration unconfirmed |
| Output DC offset, TP8 relative to TP2 | Approximately zero with small fluctuations | No numerical value or fluctuation range supplied. Do not write exactly 0.000 mV or invent an uncertainty |
| Output connection/load | Keysight oscilloscope, high-impedance setting | User believes 1 MOhm; explicit setting confirmation still pending. Previously established direct BNC cable with 1:1 scope attenuation; reconfirm for this acquisition |
| Ambient temperature | Not measured | No assumed room temperature |
| 1/5/10/20-minute frequency and Vpp series | Not provided | Blank selected annotation contains no results; do not infer stability/drift from separate observations |
| Startup observation | Appears to settle very quickly; user estimates within seconds | Qualitative observation only. Startup settling time not measured; no ten-cycle success count, off interval or cold/warm conditions supplied |

### Report treatment

- Use the voltages, frequency, amplitude and coarse supply currents above as user-reported measured hardware results, with their qualifications.
- State output DC offset as approximately zero on the multimeter, with no numerical bound established.
- Describe startup as visually rapid, without a quantified settling-time claim. Do not record ten successful starts unless the user supplies that result.
- Do not mark the warm-up stability test complete.
- Do not claim SFDR, THD, noise acceptance or metrological validation from these readings.

### Open evidence and issues

1. Record actual DC offset in mV and the observed fluctuation range if available.
2. Confirm scope input impedance and attenuation for this measurement.
3. Collect the stability time series and startup-cycle results if performed.
4. Resolve the previously reported vertical waveform movement; no resolution was confirmed with this entry.
5. Resolve the earlier scope cycle-average reading of about -58 mV versus the multimeter's approximately zero result. Instrument offset was a hypothesis, not an established cause.
6. Obtain spectral recordings/FFT settings and measurement-system residual evidence before judging the 75 dBc minimum or 80 dBc goal.

Earlier conversation context: first powered testing established output adjustment to approximately zero and a maximum around 4.62 Vpp; previous scope frequency observations were around 10.003–10.006 kHz. These separate observations are not a controlled drift measurement and are not averaged into this entry.

## Output-amplitude sweep recorded 20 November 2026

Source: user-supplied screenshot of a seven-row table. The user explicitly identifies column 1 as Vpk and column 2 as Vpp. Column 3 is interpreted as frequency in Hz and column 4 as estimated SFDR in dBc from the immediately preceding measurement discussion; these latter column headings require user confirmation. Decimal comma in 85,3 is transcribed as 85.3. All values below are reported hardware readings, not independently acquired or calibrated by the assistant.

| Output Vpk (V) | Output Vpp (V) | Frequency (Hz), heading inferred | Estimated SFDR (dBc), heading inferred |
|---|---|---|---|
| 2.20 | 4.40 | 10006.22 | 91 |
| 1.94 | 3.88 | 10006.20 | 85.3 |
| 1.76 | 3.52 | 10006.19 | 82 |
| 1.44 | 2.88 | 10006.26 | 79 |
| 0.87 | 1.74 | 10006.28 | 74.5 |
| 0.46 | 0.92 | 10006.38 | 72.8 |
| 0.25 | 0.50 | 10006.32 | 70.5 |

### Conditions and interpretation

- Measurement discussion used NI myDAQ AI0, direct BNC breakout, AI0 minus linked to AGND, with the oscilloscope disconnected. Laptop was running on battery. Confirm these conditions apply to every row.
- Proposed analyzer settings were +/-10 V input, 200 kS/s, 3200 lines, Blackman-Harris window, RMS exponential averaging with 5 averages. Actual sweep settings, software version, warm-up duration, rails and output loading have not been confirmed for this table.
- The immediately preceding advice defined a preliminary SFDR estimate over 100 Hz to 90 kHz, excluding DC and the fundamental main lobe. Confirm that this band and procedure were actually used for all rows. This is not evidence of SFDR through 100 kHz or below 100 Hz.
- User subsequently confirmed that Vpp was calculated as twice Vpk, not separately measured.
- Frequency spans 10006.19 to 10006.38 Hz across these amplitude settings (0.19 Hz total observed spread). This is an amplitude sweep, not a timed stability test or a measurement-accuracy statement.
- The fourth-column values remain preliminary system estimates. No raw spectra, fundamental/spur cursor levels, spur frequencies, repeated captures or analyzer residual qualification accompany this table. Do not certify oscillator-only SFDR or an acceptance PASS from these numbers alone.

### Supply-related spectral investigation, user-reported 20 November

- An approximately 100 kHz edge feature was observed at 200 kS/s. It persisted with PCB supply outputs OFF but the Delta main switch ON and power leads attached.
- Replacing leads did not reliably remove the feature. Turning the Delta main switch OFF made the feature disappear. This implicates a supply-associated interference path; its physical source, true frequency, possible aliasing and coupling mechanism remain unproven.
- A shorted myDAQ input baseline had no corresponding prominent edge feature. This baseline is not a measurement of analyzer distortion with a full-scale 10 kHz signal.
- A roughly 19 kHz non-harmonic peak was also reported. Exact frequency, amplitude and source remain unconfirmed. Non-harmonic discrete tones count in SFDR when inside the stated band.
- No powered-off spectrum was subtracted. The 100 kHz feature cannot be reliably qualified at the Nyquist endpoint of a 200 kS/s acquisition. Restricting the reported band must be explicit and does not resolve the interference or potential aliasing within that band.

### Evidence still needed for final spectral reporting

1. Confirm the inferred frequency and SFDR headings, actual measurement band, acquisition settings and whether Vpp was measured or calculated.
2. Supply an original spectrum/export showing the fundamental level, largest spur level and its frequency for each claimed SFDR result; preferably raw time-domain recordings with sample rate.
3. Record the test conditions (warm-up, actual rails, load, instrument/software identifiers) and repeat the maximum-output capture three times at unchanged settings to assess repeatability.
4. Qualify measurement-system residual/interference before claiming intrinsic oscillator SFDR; otherwise retain the preliminary system-estimate limitation.

## Repeat captures and assembly photographs received 20 November 2026

User confirmed 10 minutes of warm-up and that the Keysight oscilloscope was neither used nor connected during the SFDR experiment. User confirmed all tabulated Vpp values were calculated as 2 x Vpk. These confirmations supersede the corresponding unknowns above.

Original supplied files preserved in `reports/evidence/2026-11-20/`: `repeat-01.png`, `repeat-02.png`, `repeat-03.png`, `assembled-bottom.jpeg`, `assembled-top.jpeg`.

| Capture | Displayed fundamental (Hz) | Vpk (V) | Calculated Vpp (V) | Displayed cursor difference (dB) | Displayed cursor frequency separation (Hz) | Displayed SINAD (dB) |
|---|---|---|---|---|---|---|
| 1 | 10006.08 | 2.20 | 4.40 | 90.67 | 30433.56 | 70.52 |
| 2 | 10006.27 | 2.20 | 4.40 | 89.70 | 30433.56 | 70.78 |
| 3 | 10006.29 | 2.20 | 4.40 | 90.58 | 30433.56 | 70.73 |

Settings visible in all three screenshots: NI ELVISmx Dynamic Signal Analyzer, device myDAQ1, source AI0, +/-10 V range, frequency span 90000 Hz, 3200 lines, Blackman-Harris window, RMS exponential averaging, 5 averages, immediate trigger, dB/RMS display and continuous acquisition. Actual sample-rate footer is **180.18 kS/s**, not the previously proposed 200 kS/s. Displayed fundamental power is 2.41 Vrms squared. Displayed THD 0.00% is rounded and must not be reported as zero distortion.

The cursor-difference mean is 90.32 dB, range 89.70 to 90.67 dB (0.97 dB observed range); this describes three screenshots, not independent raw records or a calibrated uncertainty. Frequency range is 10006.08 to 10006.29 Hz. Time spacing between captures and averaging-history independence are unknown.

### Critical interpretation for the report

- These are two-cursor amplitude differences, not an automatically validated SFDR result. Cursor frequency separation 30433.56 Hz is NOT the spur frequency. From cursor positions, the selected component is approximately 40.4 kHz, with the other cursor near the 10 kHz fundamental.
- Other visible features, including near 80 kHz, must be compared against the selected component before claiming it is the largest spur. Full-band maximum-spur selection is not demonstrated by these screenshots alone. Accordingly report approximately 90 dB selected-component separation, with overall SFDR unverified unless maximum-spur selection is substantiated.
- The strong skirt surrounding the fundamental also needs a defined carrier exclusion region; do not silently exclude arbitrary nearby frequencies. Proposed 100 Hz to 90 kHz reporting remains subject to this and the usable upper-frequency boundary. At displayed Fs = 180.18 kS/s, Nyquist is about 90.09 kHz, so 90 kHz is very near the sampling boundary; no anti-alias qualification is established.
- No raw waveform or spectrum export or measurement-system distortion qualification supplied. The report can be completed with these limitations clearly stated, but cannot certify intrinsic >=75 or >=80 dBc SFDR from this evidence alone.
- The photographs document both sides of the assembled R1 board with mounting standoffs. They are assembly evidence, not proof of every solder joint, electrical connection or freedom from shorts.

Enough evidence is now available to write a factual implementation and preliminary performance report using the existing design/simulation records and reported hardware data. Missing timed stability, quantified startup, exact ambient temperature, numerical DC offset and analyzer residual tests should be explicitly marked not measured/unavailable rather than invented.

## Breadboard comparison supplied 20 November 2026

User identifies the following screenshot as measurements from the breadboard prototype, supplied for comparison. Original preserved as `reports/evidence/2026-11-20/breadboard-comparison-table.png`. Acquisition date and full historical setup are not established by this table. Its original heading explicitly says cursor separation, not validated SFDR. Approximate Vpp is twice displayed Vpk.

| Displayed Vpk (V) | Approximate Vpp (V) | Detected frequency (Hz) | Cursor separation (dB) |
|---|---|---|---|
| 2.49 | 4.98 | 10052.83 | 88.79 |
| 2.35 | 4.70 | 10052.83 | 89.32 |
| 2.20 | 4.40 | 10052.85 | 91.08 |
| 1.94 | 3.88 | 10052.87 | 89.93 |
| 1.76 | 3.52 | 10052.89 | 88.06 |
| 1.44 | 2.88 | 10052.91 | 89.62 |
| 0.87 | 1.74 | 10052.92 | 89.01 |
| 0.46 | 0.92 | 10052.91 | 86.72 |
| 0.25 | 0.50 | 10052.91 | 82.70 |

### Comparison at matched amplitude

| Approximate Vpp (V) | Breadboard cursor separation (dB) | PCB sweep reported estimate (dB) | PCB minus breadboard (dB) |
|---|---|---|---|
| 4.40 | 91.08 | 91.0 | -0.08 |
| 3.88 | 89.93 | 85.3 | -4.63 |
| 3.52 | 88.06 | 82.0 | -6.06 |
| 2.88 | 89.62 | 79.0 | -10.62 |
| 1.74 | 89.01 | 74.5 | -14.51 |
| 0.92 | 86.72 | 72.8 | -13.92 |
| 0.50 | 82.70 | 70.5 | -12.20 |

At 4.40 Vpp, the historical breadboard frequency is 10052.85 Hz (+0.5285% from 10 kHz) and the PCB sweep frequency is 10006.22 Hz (+0.0622%). The PCB is 46.63 Hz closer to nominal for this comparison. This is not proof of improved temperature stability or lower drift.

At 4.40 Vpp the PCB three-capture cursor separation mean (90.32 dB, range 89.70 to 90.67 dB) is numerically close to the breadboard's single 91.08 dB result, without a defensible uncertainty or equivalence claim. At lower amplitudes the reported PCB separation estimates are smaller. Do not claim the PCB improved SFDR: differing selected spur frequencies, measurement bandwidth, supply interference, acquisition conditions and measurement-system limitations must be considered. The original spectra/raw records and matching methodology are required to attribute differences to the board itself.

## Report scope confirmed by user

This is a solo personal engineering project, not an assessed assignment. There is no page limit or assignment rubric. Prepare the report around design provenance, simulation versus hardware evidence, implementation, assembly, testing, matched-amplitude comparisons and explicit limitations; no further rubric or page-limit request is needed.
