"""Run bounded, assumption-only PCB capacitance sensitivity cases.

The nominal hardware deck is copied into this directory and remains unchanged.
Each derivative adds only the explicitly listed shunt capacitance before .end.
"""

from pathlib import Path
import importlib.util
import json
import subprocess
import sys
import time

from PyLTSpice import RawRead


HERE = Path(__file__).resolve().parent
EXE = Path(r"C:\Users\20252928\AppData\Local\Programs\ADI\LTspice\LTspice.exe")
REFERENCE_DECK = HERE / "hardware_full_reference.net"
BASELINE_ANALYSIS = HERE.parent.parent / "reports" / "runtime-check" / "hardware_full-analysis.json"

spec = importlib.util.spec_from_file_location(
    "oscillator_measurements", HERE / "oscillator_measurements.py"
)
measure = importlib.util.module_from_spec(spec)
spec.loader.exec_module(measure)


CASES = {
    "par_ninv_5pf": {
        "assumption": "5 pF from the inverting summing node to ground",
        "added_elements": ["C_PAR_NINV N001 0 5p"],
        "pcb_nodes": ["N_INV"],
    },
    "par_limiter_1pf": {
        "assumption": "1 pF from each limiter threshold node to ground; symmetric bound",
        "added_elements": ["C_PAR_LIMP N002 0 1p", "C_PAR_LIMN N005 0 1p"],
        "pcb_nodes": ["LIM_P", "LIM_N"],
    },
    "par_filter_5pf": {
        "assumption": "5 pF from each internal Sallen-Key node to ground",
        "added_elements": ["C_PAR_FJ N011 0 5p", "C_PAR_FIN N012 0 5p"],
        "pcb_nodes": ["F_J", "F_IN"],
    },
    "par_rc_nodes_5pf": {
        "assumption": "5 pF from each of the four oscillator RC nodes to ground",
        "added_elements": [
            "C_PAR_RC1 kick 0 5p",
            "C_PAR_RC2 N006 0 5p",
            "C_PAR_RC3 N007 0 5p",
            "C_PAR_RC4 Vout 0 5p",
        ],
        "pcb_nodes": ["RC1", "RC2", "RC3", "VOUT"],
    },
}


def summarize_existing():
    baseline = json.loads(BASELINE_ANALYSIS.read_text(encoding="utf-8"))
    results = []
    for name in CASES:
        path = HERE / f"{name}-analysis.json"
        if not path.is_file():
            raise FileNotFoundError(path)
        full = json.loads(path.read_text(encoding="utf-8"))
        metrics = full["metrics"]
        results.append(
            {
                "name": full["name"],
                "assumption": full["assumption"],
                "pcb_nodes": full["pcb_nodes"],
                "added_elements": full["added_elements"],
                "saved_end_s": full["saved_end_s"],
                "metrics": {
                    key: metrics[key]
                    for key in ("freq", "Vpp", "THD", "SFDR", "SFDR_all_bins", "settled")
                },
                "delta_vs_nominal": full["delta_vs_nominal"],
                "full_analysis": path.name,
            }
        )
    baseline_metrics = baseline["metrics"]
    summary = {
        "scope": "bounded assumed shunt-capacitance sensitivity; no extracted PCB parasitics",
        "baseline": {
            "source": "reports/runtime-check/hardware_full-analysis.json",
            "metrics": {
                key: baseline_metrics[key]
                for key in ("freq", "Vpp", "THD", "SFDR", "SFDR_all_bins", "settled")
            },
        },
        "completed_cases": results,
        "incomplete_cases": [
            {
                "name": "par_limiter_5pf",
                "assumption": "5 pF from each limiter threshold node to ground; symmetric bound",
                "status": "LTspice exceeded the 300 s guard; partial waveform rejected",
                "interpretation": "numerical/runtime limitation, not evidence of circuit or hardware instability",
            }
        ],
    }
    (HERE / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


def create_deck(name, case):
    text = REFERENCE_DECK.read_text(encoding="utf-8-sig")
    if text.count(".end") != 1:
        raise RuntimeError("Reference deck must contain exactly one .end")
    additions = [
        "* Assumed layout-added capacitance sensitivity only; not PCB extraction",
        f"* {case['assumption']}",
        *case["added_elements"],
    ]
    deck = text.replace(".end", "\n".join(additions) + "\n.end")
    path = HERE / f"{name}.net"
    path.write_text(deck, encoding="utf-8")
    return path


def run_case(name, case):
    deck = create_deck(name, case)
    started = time.monotonic()
    proc = subprocess.run(
        [str(EXE), "-Run", "-b", deck.name],
        cwd=HERE,
        creationflags=subprocess.CREATE_NO_WINDOW,
        timeout=600,
        check=False,
    )
    elapsed = time.monotonic() - started
    if proc.returncode:
        raise RuntimeError(f"{name}: LTspice exit code {proc.returncode}")

    log = deck.with_suffix(".log").read_text(errors="replace")
    if "Total elapsed time:" not in log:
        raise RuntimeError(f"{name}: no completion record in log")

    raw_path = deck.with_suffix(".raw")
    raw = RawRead(raw_path, traces_to_read="*", verbose=False)
    properties = raw.get_raw_property()
    axis = raw.get_axis() + float(properties.get("Offset", 0))
    if float(axis[-1]) < 0.04999:
        raise RuntimeError(f"{name}: incomplete transient")
    metrics = measure.analyze_waveform(axis, raw.get_trace("V(vfinal)").get_wave())

    result = {
        "name": name,
        "kind": "simulation sensitivity, not PCB extraction or hardware measurement",
        "assumption": case["assumption"],
        "pcb_nodes": case["pcb_nodes"],
        "added_elements": case["added_elements"],
        "reference_deck": REFERENCE_DECK.name,
        "saved_end_s": float(axis[-1]),
        "ltspice_exit_code": proc.returncode,
        "elapsed_s": elapsed,
        "method": "same coherent 20-cycle interpolation and H2-H40 analysis as nominal validation",
        "metrics": metrics,
    }
    (HERE / f"{name}-analysis.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    return result


def main():
    for required in (EXE, REFERENCE_DECK, HERE / "OPA1656.LIB", HERE / "1N4148_ON.lib"):
        if not required.is_file():
            raise FileNotFoundError(required)

    if sys.argv[1:] == ["--summarize"]:
        summarize_existing()
        return

    baseline = json.loads(BASELINE_ANALYSIS.read_text(encoding="utf-8"))
    baseline_metrics = baseline["metrics"]
    selected = sys.argv[1:] or list(CASES)
    unknown = [name for name in selected if name not in CASES]
    if unknown:
        raise ValueError(f"Unknown case(s): {unknown}")
    results = []
    for name in selected:
        case = CASES[name]
        result = run_case(name, case)
        metrics = result["metrics"]
        result["delta_vs_nominal"] = {
            "frequency_hz": metrics["freq"] - baseline_metrics["freq"],
            "frequency_percent": 100 * (metrics["freq"] / baseline_metrics["freq"] - 1),
            "vpp_v": metrics["Vpp"] - baseline_metrics["Vpp"],
            "vpp_percent": 100 * (metrics["Vpp"] / baseline_metrics["Vpp"] - 1),
            "sfdr_db": metrics["SFDR"] - baseline_metrics["SFDR"],
            "thd_percentage_points": metrics["THD"] - baseline_metrics["THD"],
        }
        (HERE / f"{name}-analysis.json").write_text(
            json.dumps(result, indent=2), encoding="utf-8"
        )
        results.append(result)
        print(
            json.dumps(
                {
                    "name": name,
                    "freq_hz": metrics["freq"],
                    "vpp_v": metrics["Vpp"],
                    "sfdr_db": metrics["SFDR"],
                    "settled": metrics["settled"],
                    **result["delta_vs_nominal"],
                }
            ),
            flush=True,
        )

    if len(selected) == len(CASES):
        summary = {
            "scope": "bounded assumed shunt-capacitance sensitivity; no extracted PCB parasitics",
            "baseline": {
                "source": "reports/runtime-check/hardware_full-analysis.json",
                "metrics": baseline_metrics,
            },
            "cases": results,
        }
        (HERE / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
