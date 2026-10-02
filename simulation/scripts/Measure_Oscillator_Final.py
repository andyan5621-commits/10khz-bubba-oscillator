r"""Run Oscillator_Final.asc once and report Vpp, frequency and coherent SFDR.

python Measure_Oscillator_Final.py
python Measure_Oscillator_Final.py --raw path/to/Oscillator_Final.raw
"""
import argparse
import json
import shutil
import signal
import subprocess
import time
from datetime import datetime
from pathlib import Path

import psutil
from tqdm import tqdm
from PyLTSpice import SimRunner, RawRead
from spicelib.simulators.ltspice_simulator import LTspice
from oscillator_measurements import analyze_waveform

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMATIC = PROJECT_ROOT / "simulation" / "ltspice" / "Oscillator_Final.asc"
TIMEOUT = 300


def simulate():
    folder = PROJECT_ROOT / "runs" / "nominal" / datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    folder.mkdir(parents=True)
    # Use an exact snapshot: no component substitutions, added loads or sweeps.
    for filename in [SCHEMATIC.name, "OPA1656_channel.asy", "OPA1656.LIB", "1N4148_ON.lib"]:
        shutil.copy2(SCHEMATIC.parent / filename, folder / filename)
    print(f"Single simulation of {SCHEMATIC}\nSaved run: {folder}", flush=True)
    runner = SimRunner(output_folder=str(folder), verbose=False)
    netlist = runner.create_netlist(folder / SCHEMATIC.name)
    if netlist is None:
        raise RuntimeError("LTspice could not create the netlist")
    netlist = Path(netlist)
    child = subprocess.Popen(LTspice.spice_exe + ["-Run", "-b", str(netlist)],
                             cwd=folder, creationflags=subprocess.CREATE_NO_WINDOW)
    started = time.monotonic()
    try:
        process = psutil.Process(child.pid)
        process.nice(psutil.IDLE_PRIORITY_CLASS)
        process.cpu_affinity([psutil.Process().cpu_affinity()[-1]])
        with tqdm(desc="LTspice: one CPU, low priority", bar_format="{desc}: {elapsed}", mininterval=1) as progress:
            while child.poll() is None:
                if time.monotonic() - started > TIMEOUT:
                    raise TimeoutError(f"No finished simulation within {TIMEOUT} seconds")
                time.sleep(0.2)
                progress.update(0.2)
        raw_path = netlist.with_suffix(".raw")
        if child.returncode or not raw_path.exists():
            raise RuntimeError(f"LTspice failed; inspect {netlist.with_suffix('.log')}")
        return raw_path
    finally:
        if child.poll() is None:
            child.kill()
            child.wait(timeout=5)


def main():
    if hasattr(signal, "SIGBREAK"):
        signal.signal(signal.SIGBREAK, signal.default_int_handler)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, help="measure a completed LTspice raw file without rerunning it")
    args = parser.parse_args()
    raw_path = args.raw.resolve() if args.raw else simulate()
    raw = RawRead(raw_path, traces_to_read=["V(Vfinal)"], verbose=False)
    # LTspice can store time relative to the transient's save-start time.
    axis = raw.get_axis() + float(raw.get_raw_property().get("Offset", 0))
    if len(axis) < 4 or axis[-1] < 0.049999:
        raise ValueError("Transient did not reach 50 ms. Inspect the LTspice log; no valid final measurements exist.")
    result = analyze_waveform(axis, raw.get_trace("V(Vfinal)").get_wave())
    result.pop("harmonics")
    result["raw_file"] = str(raw_path)
    lines = ["OSCILLATOR_FINAL -- V(Vfinal)",
             f"Vpp  = {result['Vpp']:.6f} V",
             f"freq = {result['freq']:.3f} Hz",
             f"SFDR = {result['SFDR']:.3f} dB (harmonics 2-40)",
             f"All-bin SFDR = {result['SFDR_all_bins']:.3f} dB",
             f"THD  = {result['THD']:.6f} %",
             f"Settled = {result['settled']}",
             f"Bandwidth = {result['bandwidth_hz']:.0f} Hz; bin spacing = {result['resolution_hz']:.1f} Hz",
             "SFDR is measured in Python over the last 20 complete cycles.",
             f"Raw file: {raw_path}"]
    if not result["settled"]:
        lines.append("NOT SETTLED: these are provisional readings; extend the transient before using them.")
    summary = "\n".join(lines)
    raw_path.with_suffix(".measurements.json").write_text(json.dumps(result, indent=2, allow_nan=False))
    raw_path.with_suffix(".measurements.txt").write_text(summary)
    latest = PROJECT_ROOT / "runs" / "latest-final.measurements.txt"
    latest.parent.mkdir(parents=True, exist_ok=True)
    latest.write_text(summary)
    print("\n" + summary + f"\n\nResults saved: {latest}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped the simulation. No new measurement report was produced.")
