"""Coherent waveform measurement, copied unchanged from Oscilator.py."""

import math

import numpy as np

from scipy.interpolate import CubicSpline

from scipy.optimize import brentq

class WaveformNotReady(ValueError):
    """The transient may need more time before waveform analysis is possible."""

def analyze_waveform(time, voltage, periods=20, harmonics=40, samples_per_period=1024):
    """Analyze complete late cycles; harmonic SFDR uses harmonics 2..40."""
    if periods < 2 or harmonics < 2 or samples_per_period <= 2 * harmonics:
        raise ValueError("Need >=2 cycles, >=2 harmonics and sufficient samples per cycle")
    time = np.asarray(time, dtype=float)
    voltage = np.asarray(voltage, dtype=float)
    if time.ndim != 1 or voltage.shape != time.shape or len(time) < 4:
        raise ValueError("Invalid waveform arrays")
    if not np.all(np.isfinite(time)) or not np.all(np.isfinite(voltage)):
        raise ValueError("Non-finite waveform samples")
    if np.any(np.diff(time) < 0):
        raise ValueError("Waveform time is not increasing")
    # Only the final 10 ms is relevant, retaining one preceding sample.
    first = max(0, np.searchsorted(time, time[-1] - 0.010) - 1)
    time, voltage = time[first:], voltage[first:]
    keep = np.r_[True, np.diff(time) > 0]
    time, voltage = time[keep], voltage[keep]
    if np.any(np.diff(time) <= 0):
        raise ValueError("Waveform time is not increasing")
    if np.ptp(voltage) < 1e-3:
        raise WaveformNotReady("Oscillation is absent or below 1 mVpp")
    spline = CubicSpline(time, voltage)
    extrema = spline.derivative().roots(extrapolate=False)

    def voltage_limits(start, end):
        # Include interpolated extrema, so the sampling grid cannot miss peaks.
        points = np.r_[start, extrema[(extrema > start) & (extrema < end)], end]
        values = spline(points)
        return float(np.min(values)), float(np.max(values))

    level = 0.5 * (np.max(voltage) + np.min(voltage))
    crossings = np.flatnonzero((voltage[:-1] <= level) & (voltage[1:] > level))
    if len(crossings) < 2 * periods + 1:
        raise WaveformNotReady(f"Need {2 * periods} complete late cycles to check settling")
    crossings = crossings[-(2 * periods + 1):]
    edges = np.array([brentq(lambda x: float(spline(x) - level), time[i], time[i + 1],
                            xtol=1e-15) for i in crossings])

    def measure_window(start, end):
        frequency = periods / (end - start)
        if np.max(np.diff(time)) * frequency * 2 * harmonics >= 1:
            raise ValueError("Saved samples are too sparse for the requested harmonic bandwidth")
        count = periods * samples_per_period
        grid = start + np.arange(count) * ((end - start) / count)
        wave = spline(grid)
        spectrum = 2 * np.abs(np.fft.rfft(wave)) / count
        amplitudes = spectrum[np.arange(1, harmonics + 1) * periods]
        fundamental = float(amplitudes[0])
        if fundamental <= 0:
            raise ValueError("No measurable fundamental")
        relative = amplitudes / fundamental
        largest_spur = float(np.max(relative[1:]))
        # Check all resolved Fourier bins too; this includes non-harmonic spurs.
        all_spurs = spectrum[1:harmonics * periods + 1].copy()
        all_spurs[periods - 1] = 0
        broadband_spur = float(np.max(all_spurs) / fundamental)
        vmin, vmax = voltage_limits(start, end)
        return {
            "freq": float(frequency), "Vpp": vmax - vmin,
            "Vmax": vmax, "Vmin": vmin,
            "THD": float(100 * np.sqrt(np.sum(relative[1:] ** 2))),
            "SFDR": -20 * math.log10(max(largest_spur, np.finfo(float).tiny)),
            "SFDR_all_bins": -20 * math.log10(max(broadband_spur, np.finfo(float).tiny)),
            "largest_spur": largest_spur,
            "largest_harmonic": int(np.argmax(relative[1:]) + 2),
            "largest_spur_frequency": float((np.argmax(all_spurs) + 1) * frequency / periods),
            "resolution_hz": float(frequency / periods),
            "bandwidth_hz": float(harmonics * frequency),
            "harmonics": {n: {"frequency": float(n * frequency),
                              "fourier": float(amplitudes[n - 1]),
                              "normalized": float(relative[n - 1])}
                          for n in range(1, harmonics + 1)},
            "window_start": float(start), "window_end": float(end),
        }

    previous = measure_window(edges[0], edges[periods])
    result = measure_window(edges[periods], edges[-1])
    result["amplitude_drift"] = abs(result["Vpp"] / previous["Vpp"] - 1)
    result["frequency_drift"] = abs(result["freq"] / previous["freq"] - 1)
    result["sfdr_change_db"] = abs(result["SFDR"] - previous["SFDR"])
    result["settled"] = (result["amplitude_drift"] <= 1e-5
                         and result["frequency_drift"] <= 1e-7
                         and result["sfdr_change_db"] <= 0.2)
    # Preserve the original amplitude constraint across the entire final 10 ms,
    # rather than allowing an earlier peak to disappear from the 20-cycle window.
    result["Vpp_window"] = result["Vpp"]
    result["Vmin"], result["Vmax"] = voltage_limits(max(time[0], time[-1] - 0.010), time[-1])
    result["Vpp"] = result["Vmax"] - result["Vmin"]
    return result


def read_measurements(raw_file, node="V(Vfinal)", stop_time=0.05):
    """Read a completed simulation; return Vpp [V], freq [Hz], SFDR [dB], and THD [%].

    Pass the .raw path returned by runner.run_now(net), or its matching .log path.
    No simulation is launched and no JSON report is required.
    SFDR uses harmonics 2-40; SFDR_all_bins also checks other resolved bins.
    Incomplete, stepped or unsettled simulations raise an error.
    Set stop_time to match the simulation's requested end time (default 50 ms).
    """
    from pathlib import Path
    from PyLTSpice import RawRead

    if not math.isfinite(stop_time) or stop_time <= 0:
        raise ValueError("stop_time must be a positive finite number of seconds")
    raw_file = Path(raw_file)
    if raw_file.suffix.lower() == ".log":
        raw_file = raw_file.with_suffix(".raw")
    raw = RawRead(raw_file, traces_to_read=[node], verbose=False)
    properties = raw.get_raw_property()
    if "stepped" in properties.get("Flags", "").lower():
        raise ValueError("Use one simulation per raw file; stepped files are not supported")
    time = raw.get_axis() + float(properties.get("Offset", 0))
    if len(time) < 4 or time[-1] < stop_time - 1e-9:
        raise WaveformNotReady(f"Simulation did not reach {stop_time:g} seconds; check its log")
    result = analyze_waveform(time, raw.get_trace(node).get_wave())
    if not result["settled"]:
        raise WaveformNotReady("Oscillation has not settled; increase the transient duration")
    return {key: result[key] for key in
            ["Vpp", "freq", "SFDR", "SFDR_all_bins", "THD", "settled"]}
