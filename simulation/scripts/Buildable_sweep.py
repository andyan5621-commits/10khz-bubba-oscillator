"""Ordinary LTspice sweep using resistor combinations from my stock.

python Buildable_sweep.py --dry-run    # list the grid without simulating
python Buildable_sweep.py --check      # reproduce the tested fixed design
python Buildable_sweep.py              # run the full grid below
"""
import argparse
import json
import math
import shutil
import signal
import subprocess
import time
from collections import Counter
from datetime import datetime
from itertools import combinations_with_replacement
from pathlib import Path

import numpy as np
import psutil
from tqdm import tqdm
from PyLTSpice import SimRunner, SpiceEditor, RawRead
from spicelib.simulators.ltspice_simulator import LTspice
from oscillator_measurements import analyze_waveform, WaveformNotReady

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMATIC = PROJECT_ROOT / "simulation" / "ltspice" / "Oscillator.asc"
OUTPUT_ROOT = PROJECT_ROOT / "runs" / "buildable_sweep"

# ----------------------------
# Original ideal design centres
# ----------------------------
R_centre = 1544.6
RG_centre = 100e3
K_centre = 4.08
RL_centre = 1.3e6
Q_centre = 2.5
Rfilter_centre = 1935
R11_centre = 3050

# ----------------------------
# Values to sweep -- edit these lists
# ----------------------------
# A small starting grid: original centres plus the tested working values.
# Scale 0.1 reduces RG and the diode-bias resistors by ten. Capacitors do not scale.
# Add intermediate values if wanted; each extra entry increases the grid size.
# Test the known working combination first so an interrupted sweep is still useful.
scale_values = [0.1, 1.0]
R_values = [1647, R_centre]
K_values = [4.8, K_centre]
RL_values = [RL_centre]
Q_values = [Q_centre]
Rfilter_values = [1900, Rfilter_centre]
R11_values = [1 / (1 / 2000 + 1 / 100000), R11_centre]

# For example, replace a list with a wider range around its original centre:
# K_values = [4.06, 4.08, 4.10, 4.2, 4.5, 4.7, 4.8]
# RL_values = [1.2e6, 1.3e6, 1.4e6]
# Q_values = [2.3, 2.5, 2.7]
# R_values = [1520, 1544.6, 1570, 1600, 1647]

# Fixed purchased components; never swept.
CAPACITORS = {"C1": 10e-9, "C2": 10e-9, "C3": 10e-9,
              "C4": 10e-9, "C5": 1e-9, "C6": 68e-9}
STOCK = [3300, 10000, 680, 6800, 1000000, 680000, 470000, 300000,
         220000, 100000, 68000, 51000, 47000, 20000, 5100, 4700,
         2200, 2000, 510, 470, 330, 270, 220, 150, 200, 100, 47, 22, 10, 1000]
STOCK_QUANTITY = 20
MAX_SERIES_PARTS = 4
MIN_SFDR = 75
STOP_TIMES = [0.05, 0.10]  # retry longer only if the waveform is not yet settled
MAX_TIMESTEP = 100e-9
SIM_TIMEOUT = 180         # seconds per LTspice attempt, including difficult models

# ----------------------------
# Make physically buildable resistor values
# ----------------------------
def resistor_combinations():
    """Series networks of 1..4 resistors and parallel pairs, plus exact centre recipes."""
    pool = {}

    def add(parts, connection="series"):
        value = (sum(parts) if connection == "series"
                 else 1 / sum(1 / r for r in parts))
        recipe = {"value": float(value), "parts": list(parts), "connection": connection}
        key = round(value, 8)
        if key not in pool or len(parts) < len(pool[key]["parts"]):
            pool[key] = recipe

    for number in range(1, MAX_SERIES_PARTS + 1):
        for parts in combinations_with_replacement(sorted(STOCK), number):
            add(parts)
    for parts in combinations_with_replacement(sorted(STOCK), 2):
        add(parts, "parallel")
    # Exact original/reference values which need more than four series parts.
    add([300000, 100000, 6800, 1000, 200])       # 408k
    add([1000000, 1000000, 1000000, 220000, 20000, 10000])  # 3.25M
    add([300000, 20000, 4700, 200, 100])        # 325k
    return list(pool.values())


def nearest_resistor(target, pool):
    # Pick the closest achievable value, then prefer fewer physical resistors.
    if not math.isfinite(target) or target <= 0:
        raise ValueError("Resistor targets must be finite and positive")
    return min(pool, key=lambda r: (abs(r["value"] - target), len(r["parts"])))


def make_design(RVal, RGVal, KVal, RLVal, QVal, RfilterVal, R11Val, pool):
    targets = {**{f"R{i}": RVal for i in range(1, 5)},
               "R_G": RGVal, "R_F": RGVal * KVal,
               "R5": RLVal, "R7": RLVal, "R6": RLVal * QVal, "R8": RLVal * QVal,
               "R9": RfilterVal, "R10": RfilterVal, "R11": R11Val, "R12": 1000}
    recipes = {name: nearest_resistor(value, pool) for name, value in targets.items()}
    # Count the entire circuit, including four timing stages and both bias branches.
    used = Counter(part for recipe in recipes.values() for part in recipe["parts"])
    if any(count > STOCK_QUANTITY for count in used.values()):
        return None
    values = {name: recipe["value"] for name, recipe in recipes.items()}
    return {"targets": targets, "resistors": values, "recipes": recipes,
            "stock_used": dict(used), "K": values["R_F"] / values["R_G"],
            "RL": values["R5"], "Q": values["R6"] / values["R5"]}


def sweep_designs(pool, check=False):
    scales = [0.1] if check else scale_values
    Rs = [1647] if check else R_values
    Ks = [4.8] if check else K_values
    RLs = [1.3e6] if check else RL_values
    Qs = [2.5] if check else Q_values
    filters = [1900] if check else Rfilter_values
    dividers = [1 / (1 / 2000 + 1 / 100000)] if check else R11_values
    designs = []
    seen = set()
    rejected = 0

    # Normal nested loops, just like the original sweep.
    for Scale in scales:
        for RVal in Rs:
            for KVal in Ks:
                for RLVal in RLs:
                    for QVal in Qs:
                        for RfilterVal in filters:
                            for R11Val in dividers:
                                design = make_design(RVal, RG_centre * Scale, KVal,
                                                     RLVal * Scale, QVal, RfilterVal, R11Val, pool)
                                if design is None:
                                    rejected += 1
                                    continue
                                key = tuple(round(v, 8) for v in design["resistors"].values())
                                if key not in seen:
                                    designs.append(design)
                                    seen.add(key)
    return designs, rejected


def cost_function(r):
    # Original cost formula, with settling and the requested 75 dB target checked first.
    freq = r["freq"]
    Vpp = r["Vpp"]
    THD = r["THD"]
    SFDR = r["SFDR"]
    if not all(math.isfinite(v) for v in [freq, Vpp, THD, SFDR, r["SFDR_all_bins"]]):
        return float("inf")
    if not r["settled"] or r["SFDR_all_bins"] < MIN_SFDR:
        return float("inf")
    if Vpp > 5.0 or Vpp < 4.85 or abs(freq - 10000) > 50:
        return float("inf")
    cost = -SFDR
    cost += ((Vpp - 4.95) / 0.05)**2
    cost += ((freq - 10000) / 10)**2
    cost += 2 * THD
    return cost


def run_ltspice(netlist, progress=None):
    # A single owned process makes Ctrl+C and timeouts predictable.
    child = subprocess.Popen(LTspice.spice_exe + ["-Run", "-b", str(netlist)],
                             cwd=str(netlist.parent), creationflags=subprocess.CREATE_NO_WINDOW)
    started = time.monotonic()
    try:
        # Set limits on LTspice itself; a child can start at Normal priority
        # even when the parent Python process is Below Normal.
        simulation = psutil.Process(child.pid)
        simulation.nice(psutil.IDLE_PRIORITY_CLASS)
        simulation.cpu_affinity([psutil.Process().cpu_affinity()[-1]])
        last_update = -1
        while child.poll() is None:
            elapsed = time.monotonic() - started
            if elapsed > SIM_TIMEOUT:
                raise TimeoutError(f"LTspice exceeded {SIM_TIMEOUT} seconds")
            if progress is not None and elapsed - last_update >= 1:
                progress.set_postfix_str(f"LTspice running | {elapsed:.0f}s elapsed | low priority, 1 CPU")
                last_update = elapsed
            time.sleep(0.2)
        if child.returncode != 0 or not netlist.with_suffix(".raw").exists():
            raise RuntimeError(f"LTspice failed; see {netlist.with_suffix('.log')}")
    finally:
        if child.poll() is None:
            child.kill()
            child.wait(timeout=5)


def simulate_design(source, design, index, output_dir, progress):
    net = SpiceEditor(source)
    for name, value in CAPACITORS.items():
        net.set_component_value(name, f"{value:.15g}")
    for name, value in design["resistors"].items():
        net.set_component_value(name, f"{value:.15g}")
    net.set_parameters(RGval=design["resistors"]["R_G"], K=design["K"], RL=design["RL"], Q=design["Q"])
    net.set_component_value("V1", 15)
    net.set_component_value("V2", 15)
    net.remove_Xinstruction(r"(?i)^\s*\.(tran|four|meas|measure|save|options|ic)\b")
    net.add_instruction(".options plotwinsize=0 numdgt=15 reltol=1e-6 vntol=1e-9 abstol=1e-12 threads=1 method=gear")
    net.add_instruction(".save V(Vout) V(Vfiltered) V(Vfinal)")
    net.add_instruction(".temp 27")
    # The short pulse only starts the simulation; it is OFF throughout measurement.
    if "IKICK" in net.get_components("I"):
        net.set_component_value("IKICK", "PULSE(0 1m 10u 10n 10n 1u 1)")
    else:
        net.add_instruction("IKICK 0 kick PULSE(0 1m 10u 10n 10n 1u 1)")
    net.add_instruction("RSCOPE Vfinal 0 1Meg")
    net.add_instruction("CSCOPE Vfinal 0 20p")
    net.add_instruction("XSPARE 0 spare Vcc Vss spare OPA1656")
    for chip in range(1, 5):
        net.add_instruction(f"CBP{chip} Vcc 0 100n")
        net.add_instruction(f"CBN{chip} Vss 0 100n")
    net.add_instruction("CBULKP Vcc 0 10u")
    net.add_instruction("CBULKN 0 Vss 10u")

    for stop_time in STOP_TIMES:
        progress.set_postfix_str(f"K={design['K']:.3f}, RL={design['RL']/1e6:.3f}M, stop={stop_time*1000:.0f}ms")
        net.add_instruction(f".tran 0 {stop_time} {stop_time - 0.01:.12g} {MAX_TIMESTEP}")
        netlist = output_dir / f"design_{index:04d}_{stop_time*1000:.0f}ms.net"
        net.save_netlist(netlist)
        run_ltspice(netlist, progress)
        progress.set_postfix_str("Measuring waveform")
        raw = RawRead(netlist.with_suffix(".raw"), traces_to_read=["V(Vfinal)"], verbose=False)
        try:
            data = analyze_waveform(raw.get_axis(), raw.get_trace("V(Vfinal)").get_wave())
        except WaveformNotReady:
            continue
        if data["settled"]:
            data.pop("harmonics")
            return {**design, **data, "netlist": str(netlist), "raw_file": str(netlist.with_suffix('.raw'))}
    raise ValueError("No settled oscillation within STOP_TIMES")


def print_result(best, label):
    lines = [label, f"K    = {best['K']:.6g}", f"RL   = {best['RL']/1e6:.6g} MOhm",
             f"Q    = {best['Q']:.6g}", f"freq = {best['freq']:.3f} Hz",
             f"Vpp  = {best['Vpp']:.6f} V", f"THD  = {best['THD']:.6f} %",
             f"SFDR = {best['SFDR']:.3f} dB", f"All-bin SFDR = {best['SFDR_all_bins']:.3f} dB",
             f"cost = {best['cost']:.3f}", "", "RESISTORS TO BUILD (each labelled resistor):"]
    for name, recipe in best["recipes"].items():
        joiner = " + " if recipe["connection"] == "series" else " || "
        parts = joiner.join(f"{v:g}" for v in recipe["parts"])
        lines.append(f"{name:4s} = {recipe['value']:.9g} ohm : {parts} ohm")
    text = "\n".join(lines)
    print("\n" + text)
    return text


def main():
    if hasattr(signal, "SIGBREAK"):
        signal.signal(signal.SIGBREAK, signal.default_int_handler)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="save and print the resistor grid without running LTspice")
    parser.add_argument("--check", action="store_true", help="one known-working point through the same loops")
    parser.add_argument("--limit", type=int, help="only the first N designs; results are labelled partial")
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be at least 1")

    pool = resistor_combinations()
    designs, rejected = sweep_designs(pool, args.check)
    grid_size = len(designs)
    if args.limit:
        designs = designs[:args.limit]
    if not designs:
        raise ValueError("No stock-valid resistor combinations in the chosen grid")
    output_dir = OUTPUT_ROOT / datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    output_dir.mkdir(parents=True)
    (output_dir / "sweep_plan.json").write_text(json.dumps(designs, indent=2))
    print(f"Grid: {grid_size} unique stock-valid designs; scheduled: {len(designs)}; stock-rejected: {rejected}")
    print("Targets are snapped to the nearest buildable value. See sweep_plan.json for targets AND actual values.")
    print("Fixed: C1-C4=10nF, C5=1nF, C6=68nF; OPA1656; onsemi 1N4148; +/-15V.")
    print(f"Output: {output_dir}", flush=True)
    if args.dry_run:
        for i, d in enumerate(designs, 1):
            r = d["resistors"]
            print(f"{i:3d}: R={r['R1']:.6g}, RG={r['R_G']:.6g}, K={d['K']:.6g}, RL={d['RL']:.6g}, Q={d['Q']:.6g}, Rfilter={r['R9']:.6g}, R11={r['R11']:.6g}")
        return

    # Low priority, one CPU, one LTspice instance at a time.
    process = psutil.Process()
    process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    process.cpu_affinity([process.cpu_affinity()[-1]])
    # Snapshot the schematic and models; the sweep never edits the original .asc.
    snapshot = output_dir / "source.asc"
    shutil.copy2(SCHEMATIC, snapshot)
    for filename in ["OPA1656_channel.asy", "OPA1656.LIB", "1N4148_ON.lib"]:
        shutil.copy2(SCHEMATIC.parent / filename, output_dir / filename)
    runner = SimRunner(output_folder=str(output_dir), verbose=False)
    source = runner.create_netlist(snapshot)
    if source is None:
        raise RuntimeError("Could not generate the schematic netlist")
    # .lib lets LTspice read the untouched vendor models. The installed SpiceEditor
    # expands .include files and cannot rewrite TI's noiseless-resistor syntax.
    source = Path(source)
    source.write_bytes(source.read_bytes().replace(b".include ", b".lib "))
    print("One simulation at a time. Ctrl+C stops it and preserves completed results.", flush=True)
    print("The percentage counts FINISHED simulations. The first point previously took about 96 seconds.", flush=True)
    results = []
    best = None
    interrupted = False
    with (output_dir / "measurements.jsonl").open("w") as saved:
        try:
            with tqdm(total=len(designs), desc="Resistor sweep", unit="sim", dynamic_ncols=True) as progress:
                for index, design in enumerate(designs, 1):
                    started = time.monotonic()
                    tqdm.write(f"Starting run {index}/{len(designs)}: K={design['K']:.3f}, RL={design['RL']/1e6:.3f} MOhm")
                    try:
                        data = simulate_design(source, design, index, output_dir, progress)
                        cost = cost_function(data)
                        data["cost"] = cost if math.isfinite(cost) else None
                        results.append(data)
                        tqdm.write(f"Run {index}: {data['freq']:.2f} Hz, {data['Vpp']:.5f} Vpp, {data['SFDR']:.2f} dB")
                        if math.isfinite(cost) and (best is None or cost < best["cost"]):
                            best = data
                            (output_dir / "best.json").write_text(json.dumps(best, indent=2))
                            shutil.copy2(best["netlist"], output_dir / "best.net")
                    except Exception as exc:
                        data = {**design, "error": f"{type(exc).__name__}: {exc}"}
                        tqdm.write(f"Invalid run {index}: {data['error']}")
                    data["duration_seconds"] = time.monotonic() - started
                    saved.write(json.dumps(data, allow_nan=False) + "\n")
                    saved.flush()
                    progress.update(1)
        except KeyboardInterrupt:
            interrupted = True
            print("\nStopped. Completed measurements have been saved.")

    partial = interrupted or len(designs) < grid_size
    label = "REFERENCE CHECK" if args.check else ("BEST OF COMPLETED DESIGNS (PARTIAL)" if partial else "BEST DESIGN IN THIS GRID")
    if best:
        summary = print_result(best, label)
        (output_dir / "summary.txt").write_text(summary)
        print(f"\nBest circuit: {output_dir / 'best.net'}")
    else:
        if interrupted and (output_dir / "measurements.jsonl").stat().st_size == 0:
            summary = "Stopped before the first simulation finished. No complete measurements yet."
        else:
            summary = "No qualifying design found in the completed simulations. See measurements.jsonl."
        print(summary)
        (output_dir / "summary.txt").write_text(summary)
    print(f"\nResults: {output_dir}")


if __name__ == "__main__":
    main()
