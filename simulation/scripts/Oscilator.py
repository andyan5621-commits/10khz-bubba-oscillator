"""Bubba oscillator sweep with coherent, steady-state waveform measurements.

SFDR retains the original harmonic-based objective (harmonics 2..40).
SFDR_all_bins also checks non-harmonic bins up to 40*f, at f/20 resolution.
Neither metric includes circuit noise absent from the LTspice model.
"""
import argparse
import json
import math
import os
import shutil
import signal
import sys
import time
import multiprocessing as mp
from multiprocessing.connection import wait as wait_connections
import psutil
from contextlib import redirect_stdout
from io import StringIO
import re
from datetime import datetime
from itertools import product
from pathlib import Path

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.optimize import brentq
from tqdm import tqdm
from PyLTSpice import SimRunner, SpiceEditor, RawRead

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMATIC = PROJECT_ROOT / "simulation" / "ltspice" / "Oscillator.asc"
OUTPUT_ROOT = PROJECT_ROOT / "runs" / "oscillator_coherent"
MAX_TIMESTEP = 100e-9
STOP_TIMES = (0.05, 0.10, 0.20)
ACCURACY_OPTIONS = ".options plotwinsize=0 numdgt=15 reltol=1e-6 vntol=1e-9 abstol=1e-12 threads=1"

# Original ranges and ordering; RGVal remains as specified by the schematic.
K_values = np.arange(4.08, 4.281, 0.02)
RL_values = np.arange(0.5e6, 1.501e6, 0.1e6)
Q_values = np.arange(1.7, 3.501, 0.2)

def parse_ltspice_log(log_file):
    # Current LTspice logs are UTF-8; older versions may use UTF-16
    # or the Windows code page. Decode explicitly so degree signs match.
    raw = Path(log_file).read_bytes()
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        text = raw.decode("utf-16")
    elif b"\x00" in raw[:100]:
        text = raw.decode("utf-16-le")
    else:
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = raw.decode("cp1252")

    result = {}

    # Frequency
    m = re.search(r"freq:.*?=([+-]?[0-9.eE+-]+)", text)
    if m:
        result["freq"] = float(m.group(1))

    # Vpp
    m = re.search(r"vpp:.*?=([+-]?[0-9.eE+-]+)", text)
    if m:
        result["Vpp"] = float(m.group(1))

    # Vmax
    m = re.search(r"vmax:.*?=([+-]?[0-9.eE+-]+)", text)
    if m:
        result["Vmax"] = float(m.group(1))

    # Vmin
    m = re.search(r"vmin:.*?=([+-]?[0-9.eE+-]+)", text)
    if m:
        result["Vmin"] = float(m.group(1))

    # THD
    m = re.search(
        r"Total Harmonic Distortion:\s*([0-9.eE+-]+)%",
        text
    )
    if m:
        result["THD"] = float(m.group(1))

    # Harmonic table
    harmonics = {}

    pattern = re.compile(
        r"^\s*(\d+)\s+"          # harmonic number
        r"([0-9.eE+-]+)\s+"      # frequency
        r"([0-9.eE+-]+)\s+"      # Fourier component
        r"([0-9.eE+-]+)\s+"      # normalized component
        r"([+-]?[0-9.]+)°",      # phase
        re.MULTILINE
    )

    for match in pattern.finditer(text):
        n = int(match.group(1))

        harmonics[n] = {
            "frequency": float(match.group(2)),
            "fourier": float(match.group(3)),
            "normalized": float(match.group(4)),
            "phase": float(match.group(5))
        }

    result["harmonics"] = harmonics

    # Calculate SFDR
    if harmonics:
        spur_values = [
            h["normalized"]
            for n, h in harmonics.items()
            if n != 1
        ]

        if spur_values:
            largest_spur = max(spur_values)

            result["largest_spur"] = largest_spur
            result["SFDR"] = (-20 * math.log10(largest_spur)
                              if largest_spur > 0 else float("inf"))

    return result

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


def analyze_raw(raw_file, **kwargs):
    raw = RawRead(raw_file, traces_to_read=["V(n004)"], verbose=False)
    return analyze_waveform(raw.get_axis(), raw.get_trace("V(n004)").get_wave(), **kwargs)


def cost_function(r):
    """
    Lower cost = better design.
    """

    freq = r["freq"]
    Vpp  = r["Vpp"]
    THD  = r["THD"]
    SFDR = r["SFDR"]

    # Failed/undefined measurements cannot be ranked as valid designs.
    if not all(math.isfinite(value) for value in (freq, Vpp, THD, SFDR)):
        return float("inf")

    # ----------------------------
    # Hard requirements
    # ----------------------------

    # Must never exceed assignment maximum
    if Vpp > 5.0:
        return float("inf")

    # Reject designs too far from 10 kHz
    if abs(freq - 10000) > 50:
        return float("inf")

    # Reject designs with too little output amplitude
    if Vpp < 4.85:
        return float("inf")

    # ----------------------------
    # Optimization objective
    # ----------------------------

    cost = 0

    # Main goal: maximize SFDR
    # Lower cost is better -> negative SFDR
    cost -= SFDR

    # Prefer amplitude near 4.95 Vpp
    cost += ((Vpp - 4.95) / 0.05)**2

    # Prefer frequency very close to 10 kHz
    cost += ((freq - 10000) / 10)**2

    # Secondary distortion metric
    cost += 2 * THD

    return cost

def configure_measurement(net, stop_time, max_timestep=MAX_TIMESTEP):
    """Change analysis directives only; circuit and component models stay intact."""
    net.remove_Xinstruction(r"(?i)^\s*\.(tran|four|meas|measure|save|options)\b")
    # Simulate startup, but save only the final 10 ms to limit output size.
    net.add_instruction(
        f".tran 0 {stop_time:.12g} {stop_time - 0.01:.12g} {max_timestep:.12g} uic"
    )
    net.add_instruction(ACCURACY_OPTIONS)
    net.add_instruction(".save V(n004)")


def simulate_design(runner, net, K, RL, Q, run_index, progress=None, report=None):
    report = tqdm.write if report is None else report
    net.set_parameters(K=K, RL=RL, Q=Q)
    for stop_time in STOP_TIMES:
        if progress is not None:
            progress.set_postfix_str(
                f"K={K:.3f}, RL={RL/1e6:.2f}M, Q={Q:.2f}, stop={stop_time*1000:.0f}ms"
            )
        configure_measurement(net, stop_time)
        raw_file, log_file = runner.run_now(
            net, run_filename=f"Oscillator_{run_index}_{stop_time*1000:.0f}ms.net"
        )
        if raw_file is None or log_file is None:
            raise RuntimeError("LTspice did not produce simulation output")
        try:
            data = analyze_raw(raw_file)
        except WaveformNotReady as exc:
            report(f"Waveform not ready at {stop_time*1000:.0f} ms: {exc}")
            continue
        if data["settled"]:
            data.update(K=float(K), RL=float(RL), Q=float(Q),
                        stop_time=stop_time, raw_file=str(raw_file))
            return data
        report(
            f"Not settled at {stop_time*1000:.0f} ms: K={K:.3f}, "
            f"RL={RL/1e6:.2f}M, Q={Q:.2f}; "
            f"amplitude drift={data['amplitude_drift']:.2g}, "
            f"frequency drift={data['frequency_drift']:.2g}, "
            f"SFDR change={data['sfdr_change_db']:.3g} dB"
        )
    raise ValueError("Did not pass settling checks by 200 ms; excluded from ranking")


def print_measurements(data):
    print(f"freq = {data['freq']:.6f} Hz (late complete cycles)")
    print(f"Vpp  = {data['Vpp']:.6f} V (final 10 ms)")
    print(f"THD  = {data['THD']:.6f} % (harmonics 2..40)")
    print(f"SFDR = {data['SFDR']:.3f} dB (harmonic; used in original cost)")
    print(f"Largest harmonic = H{data['largest_harmonic']}")
    print(f"All-bin SFDR = {data['SFDR_all_bins']:.3f} dB "
          f"(up to {data['bandwidth_hz']/1000:.1f} kHz; "
          f"{data['resolution_hz']:.1f} Hz resolution)")
    print(f"Settling check = {'passed' if data['settled'] else 'FAILED'}")


def run_design_worker(job, netlist_file, output_dir):
    """Picklable Windows worker; no shared editor, runner, or result-file writes."""
    index, K, RL, Q = job
    started = time.perf_counter()
    messages = []
    common = dict(run_index=index, K=float(K), RL=float(RL), Q=float(Q),
                  worker_pid=os.getpid())
    try:
        # A separate directory per design also isolates any LTspice auxiliary files.
        run_dir = Path(output_dir) / f"design_{index:04d}"
        run_dir.mkdir(parents=True, exist_ok=True)
        runner = SimRunner(output_folder=str(run_dir), parallel_sims=1, verbose=False)
        net = SpiceEditor(netlist_file)
        data = simulate_design(runner, net, K, RL, Q, index, report=messages.append)
        data.update(common)
        cost = cost_function(data)
        data["cost"] = cost if math.isfinite(cost) else None
    except Exception as exc:
        # A bad simulation is recorded without terminating unrelated designs.
        data = dict(common, error=f"{type(exc).__name__}: {exc}")
    data["duration_seconds"] = time.perf_counter() - started
    data["messages"] = messages
    return data


def worker_loop(connection, netlist_file, output_dir, cpu_id):
    """One low-priority, single-CPU worker with an explicitly owned process ID."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    if hasattr(signal, "SIGBREAK"):
        signal.signal(signal.SIGBREAK, signal.SIG_IGN)
    process = psutil.Process()
    try:
        if sys.platform == "win32":
            process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
            process.cpu_affinity([cpu_id])
        while True:
            job = connection.recv()
            if job is None:
                break
            connection.send(run_design_worker(job, netlist_file, output_dir))
    except EOFError:
        pass
    finally:
        connection.close()


def stop_owned_worker(process):
    """Stop only this worker and its descendants, including its LTspice run."""
    if not process.is_alive():
        return
    try:
        owner = psutil.Process(process.pid)
        # Freeze the worker first so it cannot launch another simulator during cleanup.
        owner.suspend()
        descendants = owner.children(recursive=True)
        for child in reversed(descendants):
            try:
                child.kill()
            except psutil.NoSuchProcess:
                pass
        owner.kill()
        psutil.wait_procs(descendants, timeout=2)
    except psutil.NoSuchProcess:
        pass
    finally:
        process.join(timeout=2)


def iter_design_results(jobs, netlist_file, output_dir, workers):
    """Poll every 100 ms so Windows can deliver Ctrl+C even during a long run."""
    context = mp.get_context("spawn")
    owned = []
    active = {}
    remaining = iter(jobs)
    cpus = psutil.Process().cpu_affinity() if sys.platform == "win32" else [0]
    # Spread workers over the allowed CPU IDs instead of concentrating them
    # on adjacent IDs, which may be sibling hardware threads.
    worker_count = min(workers, len(jobs), len(cpus))
    worker_cpus = [cpus[slot * len(cpus) // worker_count]
                   for slot in range(worker_count)]
    cancelled = True
    try:
        for slot in range(worker_count):
            parent, child = context.Pipe()
            process = context.Process(
                target=worker_loop,
                args=(child, str(netlist_file), str(output_dir), worker_cpus[slot]),
            )
            process.start()
            child.close()
            owned.append((process, parent))
            job = next(remaining)
            parent.send(job)
            active[parent] = job
        while active:
            for connection in wait_connections(list(active), timeout=0.1):
                job = active.pop(connection)
                try:
                    data = connection.recv()
                except EOFError as exc:
                    raise RuntimeError(f"Worker exited unexpectedly while running design {job[0]}") from exc
                yield data
                job = next(remaining, None)
                if job is not None:
                    connection.send(job)
                    active[connection] = job
        cancelled = False
    finally:
        if cancelled:
            tqdm.write("Stopping this sweep's simulations now; saved measurements are retained.")
        # Ignore a second Ctrl+C while the short, bounded cleanup is in progress.
        previous_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        try:
            for process, connection in owned:
                if cancelled:
                    stop_owned_worker(process)
                else:
                    try:
                        connection.send(None)
                    except (BrokenPipeError, EOFError, OSError):
                        pass
                    process.join(timeout=2)
                    if process.is_alive():
                        stop_owned_worker(process)
                connection.close()
        finally:
            signal.signal(signal.SIGINT, previous_handler)


def positive_integer(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return number


def print_run_summary(results, total_runs, grid_size, workers, elapsed, output_dir,
                      scope, interrupted=False):
    good = [r for r in results if "error" not in r]
    failed = len(results) - len(good)
    # Preserve the original grid order when costs tie, despite random finish order.
    ranked = sorted((r for r in good if r["cost"] is not None),
                    key=lambda r: (r["cost"], r["run_index"]))
    print("=" * 76)
    print("OSCILLATOR SWEEP RESULTS")
    print(f"Finished: {datetime.now().astimezone().isoformat(timespec='seconds')}")
    print(f"Circuit: {SCHEMATIC}")
    print("Measured node: V(n004) | last 20 complete cycles | harmonics 2..40")
    print(f"Scope: {scope}" + (" [INTERRUPTED]" if interrupted else ""))
    print(f"Completed: {len(results):,}/{total_runs:,} | Full grid: {grid_size:,} | Workers: {workers}")
    print(f"Measured: {len(good)} | Failed/unsettled: {failed} | Qualifying: {len(ranked)}")
    print("CPU policy: one CPU / one solver thread per worker, low priority")
    print(f"Elapsed: {elapsed/60:.2f} min ({elapsed:.1f} s)")
    print("Limits: 4.85 <= Vpp <= 5.00 V; 9950 <= frequency <= 10050 Hz")
    if not ranked:
        if len(good) == 1:
            print_measurements(good[0])
        print("No qualifying design found in the completed simulations.")
    else:
        best = ranked[0]
        label = "BEST DESIGN" if scope == "FULL GRID" and not interrupted else "BEST OF COMPLETED DESIGNS"
        print(f"\n{label}")
        print(f"K    = {best['K']:.6g}")
        print(f"RL   = {best['RL']/1e6:.3f} MOhm")
        print(f"Q    = {best['Q']:.6g}")
        print_measurements(best)
        print(f"cost = {best['cost']:.6f}")
        print("\nTOP DESIGNS (original cost formula)")
        print("   K     RL/MOhm     Q       freq/Hz     Vpp/V     SFDR/dB      cost")
        for r in ranked[:10]:
            print(f"{r['K']:6.3f}  {r['RL']/1e6:8.3f}  {r['Q']:6.3f}  "
                  f"{r['freq']:11.3f}  {r['Vpp']:8.5f}  {r['SFDR']:9.3f}  {r['cost']:9.3f}")
    print(f"\nMeasurements: {output_dir / 'measurements.jsonl'}")
    print(f"Summary: {output_dir / 'summary.txt'}")
    print("=" * 76)


def main():
    if hasattr(signal, "SIGBREAK"):
        signal.signal(signal.SIGBREAK, signal.default_int_handler)
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--single", type=float, nargs=3, metavar=("K", "RL_OHMS", "Q"),
                      help="simulate just one design, e.g. --single 4.08 1300000 2.5")
    mode.add_argument("--analyze", type=Path, metavar="RAW_FILE",
                      help="analyze an existing raw file; its original numerical accuracy still applies")
    available_cpus = len(psutil.Process().cpu_affinity()) if sys.platform == "win32" else (os.cpu_count() or 1)
    default_workers = 2 if available_cpus >= 4 else 1
    parser.add_argument("--workers", type=positive_integer, default=default_workers,
                        help="simultaneous simulations: 2 (balanced default) or 1 (quiet); one CPU per worker")
    parser.add_argument("--limit", type=positive_integer,
                        help="quick check of the first N grid points; clearly marked as a partial sweep")
    args = parser.parse_args()
    if args.workers > 2:
        parser.error("Laptop mode allows --workers 1 (quiet) or --workers 2 (balanced)")
    if args.limit is not None and (args.single or args.analyze):
        parser.error("--limit applies only to the parameter sweep")
    if args.analyze:
        print_measurements(analyze_raw(args.analyze))
        return 0

    output_dir = OUTPUT_ROOT / datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    output_dir.mkdir(parents=True, exist_ok=False)
    print("Creating LTspice netlist...", flush=True)
    runner = SimRunner(output_folder=str(output_dir))
    netlist_file = runner.create_netlist(SCHEMATIC)
    if netlist_file is None:
        raise RuntimeError("LTspice did not create the oscillator netlist")
    # Build once in the parent, then share only an immutable saved netlist path.
    snapshot = output_dir / "source.net"
    shutil.copy2(netlist_file, snapshot)
    grid_size = len(K_values) * len(RL_values) * len(Q_values)
    parameters = [tuple(args.single)] if args.single else list(product(K_values, RL_values, Q_values))
    if args.limit is not None:
        parameters = parameters[:args.limit]
    jobs = [(i, float(k), float(rl), float(q))
            for i, (k, rl, q) in enumerate(parameters, start=1)]
    total_runs = len(jobs)
    workers = min(args.workers, total_runs, available_cpus)
    scope = "SINGLE DESIGN" if args.single else ("FULL GRID" if total_runs == grid_size else "PARTIAL GRID")
    print(f"Starting {total_runs:,} simulations with {workers} worker processes | {scope}")
    print("Laptop mode: one CPU and one LTspice solver thread per worker; low priority.")
    print("Ctrl+C stops this sweep and saves the completed-results summary.")
    print(f"Results and waveforms: {output_dir}", flush=True)
    metadata = dict(started=datetime.now().astimezone().isoformat(), schematic=str(SCHEMATIC),
                    netlist_snapshot=str(snapshot), scope=scope, grid_size=grid_size,
                    scheduled_runs=total_runs, workers=workers, max_timestep=MAX_TIMESTEP,
                    stop_times=STOP_TIMES, accuracy_options=ACCURACY_OPTIONS,
                    python=sys.version, command=sys.argv)
    (output_dir / "run_info.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    results = []
    interrupted = False
    started = time.perf_counter()
    try:
        with (output_dir / "measurements.jsonl").open("w", encoding="utf-8") as saved:
            with tqdm(total=total_runs, desc="Oscillator sweep", unit="sim",
                      dynamic_ncols=True) as progress:
                for data in iter_design_results(jobs, snapshot, output_dir, workers):
                    saved.write(json.dumps(data, allow_nan=False) + "\n")
                    saved.flush()
                    results.append(data)
                    for message in data["messages"]:
                        tqdm.write(f"Run {data['run_index']}: {message}")
                    if "error" in data:
                        tqdm.write(f"Failed run {data['run_index']}: K={data['K']:.3f}, "
                                   f"RL={data['RL']/1e6:.2f}M, Q={data['Q']:.2f}: {data['error']}")
                    failed = sum("error" in r for r in results)
                    qualifying = sum("error" not in r and r["cost"] is not None for r in results)
                    progress.set_postfix_str(
                        f"valid={qualifying}, failed={failed}, "
                        f"last K/RL/Q={data['K']:.2f}/{data['RL']/1e6:.1f}M/{data['Q']:.1f}",
                        refresh=False,
                    )
                    progress.update(1)
    except KeyboardInterrupt:
        interrupted = True
    elapsed = time.perf_counter() - started
    captured = StringIO()
    with redirect_stdout(captured):
        print_run_summary(results, total_runs, grid_size, workers, elapsed,
                          output_dir, scope, interrupted)
    summary = captured.getvalue()
    (output_dir / "summary.txt").write_text(summary, encoding="utf-8")
    print("\n" + summary, flush=True)
    metadata.update(completed_runs=len(results), elapsed_seconds=elapsed, interrupted=interrupted)
    (output_dir / "run_info.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return 130 if interrupted else 0


if __name__ == "__main__":
    mp.freeze_support()
    raise SystemExit(main())
