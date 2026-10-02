import os

# Four simulations, without extra numerical-library threads per worker.
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

from PyLTSpice import SimRunner, SpiceEditor
from oscillator_measurements import read_measurements
from spicelib.simulators.ltspice_simulator import LTspice
from itertools import product
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from threading import Event
from pathlib import Path
from datetime import datetime
import pandas as pd
from tqdm import tqdm
import shutil
import signal
import subprocess
import time

WORKERS = 4
TIMEOUT = 600  # Seconds per simulation, allowing for four simultaneous runs.
TOLERANCE = 0.01
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMATIC = PROJECT_ROOT / "simulation" / "ltspice" / "Oscillator_Final.asc"
OUTPUT_ROOT = PROJECT_ROOT / "runs" / "tolerance"


def prepare_circuit(output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename in [SCHEMATIC.name, "OPA1656_channel.asy", "OPA1656.LIB", "1N4148_ON.lib"]:
        shutil.copy2(SCHEMATIC.parent / filename, output_dir / filename)
    runner = SimRunner(output_folder=str(output_dir), verbose=False)
    netlist_file = runner.create_netlist(output_dir / SCHEMATIC.name)
    if netlist_file is None:
        raise RuntimeError("LTspice could not create the schematic netlist")
    netlist_file = Path(netlist_file)
    # LTspice reads the vendor models unchanged; SpiceEditor cannot rewrite them.
    netlist_file.write_bytes(netlist_file.read_bytes().replace(b".include ", b".lib "))
    net = SpiceEditor(netlist_file)
    net.add_instruction(".options threads=1")
    return net


def make_jobs(net, components, output_dir, prefix):
    nominal_values = {
        comp: net.get_component_floatvalue(comp)
        for comp in net.get_components() if comp.startswith(("R", "C"))
    }
    jobs = []
    # Same ordinary +/-1% combinations as before. Each gets a separate file.
    for index, signs in enumerate(product([-1, 1], repeat=len(components)), 1):
        for comp, value in nominal_values.items():
            net.set_component_value(comp, f"{value:.15g}")
        keys = dict(zip(components, signs))
        for comp, sign in keys.items():
            value = nominal_values[comp] * (1 + sign * TOLERANCE)
            net.set_component_value(comp, f"{value:.15g}")
        filename = output_dir / f"{prefix}_{index:03d}.net"
        net.save_netlist(filename)
        jobs.append((filename, keys))
    for comp, value in nominal_values.items():
        net.set_component_value(comp, f"{value:.15g}")
    return jobs


def run_simulation(filename, stop):
    # Each worker owns one separate LTspice process. No shared editor or runner.
    if stop.is_set():
        raise InterruptedError("Stopped")
    child = subprocess.Popen(
        LTspice.spice_exe + ["-Run", "-b", str(filename)],
        cwd=filename.parent,
        creationflags=subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS,
    )
    started = time.monotonic()
    try:
        while child.poll() is None:
            if stop.wait(0.2):
                raise InterruptedError("Stopped")
            if time.monotonic() - started > TIMEOUT:
                raise TimeoutError(f"Simulation exceeded {TIMEOUT}s; see {filename.with_suffix('.log')}")
        if stop.is_set():
            raise InterruptedError("Stopped")
        if child.returncode:
            raise RuntimeError(f"LTspice failed; see {filename.with_suffix('.log')}")
        return read_measurements(filename.with_suffix(".raw"))
    finally:
        if child.poll() is None:
            child.kill()
            child.wait(timeout=5)


def run_sweep(jobs, title, csv_file, nominal=None):
    results = []
    remaining = iter(jobs)
    stop = Event()
    pending = {}
    # Threads coordinate external LTspice processes; the simulations run in parallel.
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        with tqdm(total=len(jobs), desc=title, unit="sim", dynamic_ncols=True) as progress:
            try:
                while True:
                    while len(pending) < WORKERS:
                        job = next(remaining, None)
                        if job is None:
                            break
                        filename, keys = job
                        pending[pool.submit(run_simulation, filename, stop)] = job
                    if not pending:
                        break
                    progress.set_postfix(running=len(pending), refresh=False)
                    done, _ = wait(pending, timeout=0.25, return_when=FIRST_COMPLETED)
                    progress.refresh()  # Elapsed time remains visible during long runs.
                    for future in done:
                        filename, keys = pending.pop(future)
                        row = {**keys, "run": filename.stem, "status": "ok", "error": ""}
                        try:
                            data = future.result()
                            row.update({key: data[key] for key in ["freq", "Vpp", "SFDR"]})
                            if nominal is not None:
                                for key in ["freq", "Vpp", "SFDR"]:
                                    row[f"{key}_dev"] = abs(data[key] - nominal[key])
                        except Exception as exc:
                            row.update(status="failed", error=str(exc))
                            tqdm.write(f"{filename.stem}: {exc}")
                        results.append(row)
                        # Only the main thread writes the CSV, after each completion.
                        pd.DataFrame(results).sort_values("run").to_csv(csv_file, index=False)
                        progress.update(1)
            finally:
                # Ctrl+C cancels queued work and tells our active processes to exit.
                stop.set()
                for future in pending:
                    future.cancel()
    return pd.DataFrame(results).sort_values("run")


def print_worst(df, title):
    successful = df.loc[df["status"] == "ok"]
    print(f"\n{title}: {len(successful)}/{len(df)} successful simulations")
    if successful.empty:
        print("No valid measurements. Check the errors recorded in the CSV.")
        return
    for key in ["freq", "Vpp", "SFDR"]:
        print(f"\nHighest {key} deviation:")
        print(successful.loc[successful[f"{key}_dev"].idxmax()])


def main():
    if hasattr(signal, "SIGBREAK"):
        signal.signal(signal.SIGBREAK, signal.default_int_handler)
    output_dir = OUTPUT_ROOT / ("tolerance_final_" + datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    print(f"Results: {output_dir}", flush=True)
    print(f"{WORKERS} workers, one LTspice thread each. Ctrl+C stops this sweep.", flush=True)
    print("1 nominal + 256 R/C corners + 4 RG/RF corners; tolerance +/-1%.", flush=True)
    try:
        net = prepare_circuit(output_dir)
        nominal_file = output_dir / "nominal.net"
        net.save_netlist(nominal_file)
        baseline = run_sweep([(nominal_file, {})], "Nominal simulation", output_dir / "nominal.csv")
        if baseline.iloc[0]["status"] != "ok":
            raise RuntimeError(f"Nominal simulation failed: {baseline.iloc[0]['error']}")
        nominal = baseline.iloc[0].to_dict()
        print(f"\nNOMINAL: {nominal['freq']:.3f} Hz, {nominal['Vpp']:.6f} Vpp, {nominal['SFDR']:.3f} dB")

        timing_components = ["R1", "R2", "R3", "R4", "C1", "C2", "C3", "C4"]
        jobs = make_jobs(net, timing_components, output_dir, "RC")
        df = run_sweep(jobs, "R/C tolerance sweep", output_dir / "RC_sweep.csv", nominal)
        print_worst(df, "R1-R4 / C1-C4 SWEEP RESULTS")

        # make_jobs restored all timing values before preparing the gain sweep.
        jobs = make_jobs(net, ["R_G", "R_F"], output_dir, "RGRF")
        df2 = run_sweep(jobs, "RG/RF tolerance sweep", output_dir / "rgfr_sweep.csv", nominal)
        print_worst(df2, "RG / RF SWEEP RESULTS")
    except KeyboardInterrupt:
        print("\nStopped. Completed measurements are saved; this sweep's LTspice processes have stopped.")
    finally:
        print(f"\nResults: {output_dir}", flush=True)


if __name__ == "__main__":
    main()
