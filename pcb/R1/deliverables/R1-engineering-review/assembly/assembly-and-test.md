# Prototype assembly, power-up, and measurement procedure

Status: **ENGINEERING PROCEDURE — USE ONLY WITH THE REVIEWED, RELEASED BOARD REVISION**

Board revision: ______  Serial number: ______  Assembler: ______  Date: ______

## Required release data

Verify these settings against the released schematic before energizing. Blank fields elsewhere in this document are measurement records to complete during assembly and test, not unspecified design requirements.

| Parameter | Approved value |
|---|---|
| Positive rail | +15 V (recovered from archived physical design; reconfirm against released schematic) |
| Negative rail | -15 V (recovered from archived physical design; reconfirm against released schematic) |
| Initial current limit per rail | 60 mA |
| Expected current per rail | 31.2 mA op-amp quiescent typical; 40 mA datasheet maximum quiescent for eight channels over temperature; expect approximately 32–45 mA with oscillator signal currents and no external load |
| Oscillation frequency | Nominal 10 kHz. Fresh nominal model: 9,984.35 Hz; archived prototype: 10,052.83 Hz. Investigate outside 9.5–10.5 kHz during initial bring-up; record error from 10 kHz rather than interpreting this diagnostic range as a precision acceptance specification. |
| Expected output amplitude and DC offset | Pot minimum near 0 Vpp; fresh nominal full-scale model 4.642 Vpp into 1 MΩ ∥ 20 pF; archived prototype about 4.98 Vpp under its recorded conditions. Investigate output DC magnitude above 100 mV after settling. Do not adjust circuit values merely to force the model or hardware to 5 Vpp. |
| Intended output load | >1 MΩ resistive input (Alps requires output-side impedance >100× its 10 kΩ total resistance); record probe/input capacitance ______ pF |
| Potentiometer initial setting and safe range | Across VFINAL-ground; set wiper near ground before power-up; confirm terminal numbering/rotation first |
| Warm-up time before final measurement | At least 10 minutes; extend until frequency/amplitude trend is stable. Record actual time and ambient temperature. |

The archived physical design used four dual OPA1656 packages (seven active channels) on external ±15 V rails; all eight amplifier channels draw supply current. TI specifies 3.9 mA typical quiescent current per channel and 5 mA maximum across temperature, giving 31.2 mA typical and 40 mA maximum quiescent current for the four packages. A 60 mA limit per rail leaves allowance for normal 10 kHz reactive and feedback load current while still sharply limiting a board fault. The released schematic must confirm rail and supply-pin mapping before power-up.

## Incoming and pre-assembly inspection

1. Verify board revision against the approved fabrication archive and BOM.
2. Inspect board outline, holes, slots, solder mask, legend, opens/shorts, scratches, and exposed copper. Quarantine any board with uncertain damage.
3. Use a DMM to check that positive rail to ground, negative rail to ground, and rail-to-rail are not shorted. Record readings and polarity: ______.
4. Match every reserved part to its released MPN and footprint. Stop on any geometry or marking mismatch.
5. Keep OPA1656 devices under ESD control. Observe TI's pin-1 marking.

## Assembly order

1. Measure resistor values before fitting; populate the lowest-profile fixed resistors first. Check completed logical networks before adding active parts where no parallel circuit path invalidates the reading. Record the measured result beside R1–R12, RG, and RF on the build sheet. Isolate one end for an ambiguous resistance measurement; do not mistake in-circuit loading for a wrong component.
2. Confirm that each series chain is continuous and isolated from adjacent nodes. Confirm R11's 2 kΩ and 100 kΩ parts share both end nodes.
3. Fit small ceramic capacitors and diodes; verify diode cathode orientation before soldering.
4. Fit the OPA1656 devices and local 100 nF decouplers with the shortest practical ground/rail loop.
5. Fit film and electrolytic capacitors; verify electrolytic polarity.
6. Fit the approved potentiometer in its documented initial position.
7. Fit terminal block and BNC last. Check wire-entry direction, terminal labels, BNC board-edge alignment, and shield joints.
8. Clean flux as required by the flux process. Inspect every joint under magnification for bridges, insufficient wetting, disturbed joints, and solder debris.

For mechanical support, the board provides four 2.7 mm non-plated holes for M2.5 hardware. Use suitable spacers and keep screw heads/washers within the reviewed 6.0 mm diameter hardware envelope. Fasteners, spacers and an enclosure are not included in the reserved electronic-parts inventory. Check underside clearance and do not let conductive hardware bridge exposed copper or component leads. The BNC mating section projects beyond the board edge; do not use the soldered connector as the sole support for repeated cable insertion.

## Unpowered checks

- Measure resistance from each rail to ground in both DMM polarities and compare across assembled boards.
- Verify BNC shield to circuit ground and center pin to the intended output net; verify no center-to-shield short.
- Verify terminal pin order against the schematic and silkscreen.
- Check diode and electrolytic polarity from both assembly drawing and electrical continuity, not legend alone.
- Inspect all op-amp pins for bridges. Record resistance around the supply pins if the schematic provides expected values.
- Set the potentiometer only to the approved initial resistance measured wiper-to-each-end.

## Current-limited first power-up

1. Disconnect the output load and all nonessential test equipment. Set both supply outputs to 0 V and set each rail current limit to 60 mA.
2. Connect ground first, then the rail leads with the supply disabled. Independently confirm rail polarity at the PCB terminal.
3. Ramp both rails together: first to ±2.5 V, then ±5 V, ±10 V, and finally ±15 V, pausing at every step to inspect both currents and output DC. Stop immediately for current-limit operation, a sustained current above 50 mA on either rail after startup, more than 10 mA rail-to-rail current mismatch, wrong polarity, smoke, odor, rapid heating, or unexpected DC output. A brief startup transient below the 60 mA clamp is acceptable only if it settles into the expected envelope.
4. At the approved rails, record positive-rail current ______, negative-rail current ______, output DC ______, and device case temperatures after ______ min.
5. With a high-impedance oscilloscope probe, confirm startup and oscillation at the designated test points. Record frequency, waveform amplitude, DC offset, startup time, clipping, and any visible parasitic oscillation.
6. Power down before attaching or changing the specified output load. Repeat current and waveform checks with that load.

## Startup, amplitude and stability checks

1. Probe TP5 (buffered oscillator output) with a high-impedance probe and trigger from a supply rise. Measure the interval from rails reaching ±15 V until the amplitude settles within ±1% of its eventual value. Repeat ten power cycles, including a cold start and a warm restart; record every failed or delayed start. The completed 50 ms nominal simulation is evidence for one modeled startup condition, not a guaranteed hardware startup time.
2. At TP8/BNC, sweep the pot slowly across its full travel. Record minimum, midpoint and maximum Vpp, DC offset, frequency, and load. Check for discontinuities, bursts or sustained instability. Do not connect a 50 Ω scope/analyzer termination directly.
3. At the intended measurement setting, log frequency and Vpp at 1, 5, 10 and 20 minutes after power-up. Keep load, rails and probe unchanged. Record drift; compare the breadboard and PCB with the same warm-up interval and ambient conditions.
4. Use a wide-band scope check for unwanted high-frequency oscillation as well as the 10 kHz waveform. A clean narrow-band audio spectrum alone does not establish op-amp stability.

## Prototype-versus-PCB comparison

The archived result is context; a direct improvement claim requires a new matched comparison with the same instrument, load, amplitude, warm-up and analysis band.

| Quantity | Archived prototype evidence | Matched prototype repeat | New PCB |
|---|---|---|---|
| Rails / load / pot setting | ±15 V archive; recover exact test configuration | ______ | ______ |
| Frequency | 10,052.83 Hz screenshot | ______ | ______ |
| Output amplitude | 2.49 V peak, approximately 4.98 Vpp screenshot | ______ | ______ |
| Startup success / settling time | No qualified repeated-cycle record | ______ | ______ |
| 20-minute frequency / amplitude drift | Not established | ______ | ______ |
| Largest spur over stated band | H3 cursor separation 88.79 dB; not a calibrated full-band intrinsic SFDR claim | ______ | ______ |
| SFDR / THD / measurement residual | Re-measure with the method below | ______ | ______ |
| Rail currents | Not established by the archived screenshot | ______ | ______ |

## Functional measurement record

Record instrument model, serial number, calibration status, probe/fixture, termination, bandwidth limit, rail settings, ambient temperature, board revision, pot setting, warm-up time, and all software/FFT settings. Save raw waveform data as well as screenshots.

### SFDR method

Simulation values near 90.8 dB are predictions only and must not be reported as new-PCB hardware performance. The archived breadboard has historical analyzer evidence: 10,052.83 Hz fundamental and an 88.79 dB fundamental-to-H3 cursor separation near full output, measured through the potentiometer wiper with NI myDAQ settings documented in the source archive. That measurement includes setup contribution and lacks an independent residual/calibration uncertainty, so it is a reference result rather than acceptance evidence for the new PCB. New-PCB target is at least 80 dBc; the minimum acceptance threshold is 75 dBc under the documented test condition.

1. Use a spectrum/audio analyzer or a digitizer whose residual spurs have first been measured with an appropriate low-distortion source or loopback. The setup should have at least 10 dB, preferably 15–20 dB, margin below the 80 dBc target. If it does not, report only the measurement-system-limited lower bound.
2. Avoid overdriving the analyzer. Document any attenuator, buffer, transformer, filter, and termination. Confirm those items do not create or hide the dominant spur.
3. Prefer coherent sampling: choose sample rate, record length, and acquisition so the oscillator completes an integer number of cycles in the record. If coherent sampling cannot be maintained because the free-running oscillator drifts, use a suitable low-sidelobe window, capture a sufficiently long record, and report the window and equivalent noise bandwidth.
4. Ensure analog anti-alias filtering and sample rate cover every harmonic/spur included in the stated measurement band. State the lower and upper analysis frequencies.
5. Compute a calibrated power spectrum. Identify the fundamental by integrating all bins in its main lobe. Exclude DC and the fundamental main-lobe bins only; document any other excluded bins.
6. Find the largest remaining discrete spectral component in the stated band, including harmonics unless a second explicitly labeled “non-harmonic SFDR” result is also desired. Integrate the complete main lobe of that spur with the same amplitude convention.
7. Report `SFDR = 20 log10(Vfundamental,rms / Vlargest_spur,rms)` in dBc, together with fundamental frequency/amplitude, largest-spur frequency/amplitude, load, rails, bandwidth, FFT settings, and setup residual.
8. Repeat at least three acquisitions after warm-up and report the worst valid SFDR. Recheck with a changed record length or sample rate; a spur that moves as an alias or FFT artifact requires investigation.
9. Pass criterion: worst valid result ≥75 dBc. Goal met: worst valid result ≥80 dBc. Results below 75 dBc fail. Results limited by an analyzer/setup spur cannot pass.

Coherent sampling is recommended because spectral leakage can otherwise look like spurs. Analog Devices describes coherent FFT sampling for SFDR testing here: https://www.analog.com/en/resources/technical-articles/defining-and-testing-dynamic-parameters-in-highspeed-adcs-part-1.html

### THD and analysis-band record

For THD, integrate each harmonic's complete spectral main lobe using the same RMS convention as the fundamental. Compute `THD = sqrt(V2² + V3² + ... + VN²) / V1`, report percent and `20 log10(THD)` in dB, and state exactly which harmonic orders were included. This harmonic-only quantity is different from THD+N or SINAD. Do not silently include the noise floor as harmonic power.

Use an explicit analysis band compatible with the analyzer's sample rate and analog anti-alias response. For an archived-style 0–100 kHz comparison, a fundamental above 10 kHz puts its tenth harmonic beyond 100 kHz; state the resulting harmonic limit instead of claiming an H2–H10 measurement. A wider-band result is useful, but label it separately and repeat both boards with identical bandwidth. Record the largest spur even if it is not a harmonic. Preserve all raw records and rejected acquisitions with the reason for rejection.

## Build disposition

Visual inspection: PASS / FAIL  
Unpowered checks: PASS / FAIL  
Power-up: BLOCKED / PASS / FAIL  
Functional waveform: BLOCKED / PASS / FAIL  
SFDR: BLOCKED / ______ dBc; target met YES / NO; acceptance PASS / FAIL  
Open anomalies / rework: ______

