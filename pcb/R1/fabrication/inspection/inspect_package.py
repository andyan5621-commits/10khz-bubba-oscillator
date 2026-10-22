#!/usr/bin/env python3
"""Inspect an immutable KiCad fabrication review package with Gerbonara.

This script never edits the review package.  It writes reports and SVG renders
to fabrication/inspection/results (or --output) for a human release review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
KICAD_PYTHON = Path(r"C:\Program Files\KiCad\9.0\bin\python.exe")
sys.path.insert(0, str(HERE / "vendor"))

try:
    import gerbonara
    from gerbonara.layers import LayerStack
    from gerbonara.utils import MM
except ImportError as exc:  # pragma: no cover - diagnostic path
    raise SystemExit(
        "Workspace-local Gerbonara is missing. See fabrication/inspection/README.md."
    ) from exc


REQUIRED_LAYERS = {
    ("top", "copper"),
    ("bottom", "copper"),
    ("top", "mask"),
    ("bottom", "mask"),
    ("top", "silk"),
    ("bottom", "silk"),
    ("mechanical", "outline"),
}

EXPECTED_FILE_FUNCTIONS = {
    ("top", "copper"): ("Copper", "L1", "Top"),
    ("bottom", "copper"): ("Copper", "L2", "Bot"),
    ("top", "mask"): ("Soldermask", "Top"),
    ("bottom", "mask"): ("Soldermask", "Bot"),
    ("top", "silk"): ("Legend", "Top"),
    ("bottom", "silk"): ("Legend", "Bot"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bounds_dict(bounds):
    if bounds is None:
        return None
    (min_x, min_y), (max_x, max_y) = bounds
    return {
        "min_x_mm": min_x,
        "min_y_mm": min_y,
        "max_x_mm": max_x,
        "max_y_mm": max_y,
        "width_mm": max_x - min_x,
        "height_mm": max_y - min_y,
    }


def contains(outer, inner, tolerance_mm=0.15):
    if outer is None or inner is None:
        return None
    (ox0, oy0), (ox1, oy1) = outer
    (ix0, iy0), (ix1, iy1) = inner
    return (
        ix0 >= ox0 - tolerance_mm
        and iy0 >= oy0 - tolerance_mm
        and ix1 <= ox1 + tolerance_mm
        and iy1 <= oy1 + tolerance_mm
    )


def gerber_file_function(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")[:65536]
    match = re.search(r"%TF\.FileFunction,([^*]+)\*%", text)
    return tuple(part.strip() for part in match.group(1).split(",")) if match else None


def drill_file_function(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")[:65536]
    match = re.search(r"TF\.FileFunction,([^\r\n*]+)", text)
    return tuple(part.strip() for part in match.group(1).split(",")) if match else None


def verify_manifest(package: Path, failures: list[str], facts: dict):
    manifest_path = package / "SHA256.json"
    if not manifest_path.is_file():
        failures.append("SHA256.json is missing from the review package")
        facts["manifest"] = {"present": False, "verified": False}
        return

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        failures.append(f"SHA256.json cannot be read: {exc}")
        facts["manifest"] = {"present": True, "verified": False}
        return

    mismatches = []
    for relative, expected in manifest.items():
        candidate = package / relative
        if not candidate.is_file():
            mismatches.append(f"missing: {relative}")
        elif sha256(candidate) != expected:
            mismatches.append(f"hash mismatch: {relative}")
    if mismatches:
        failures.extend(f"Manifest {item}" for item in mismatches)
    facts["manifest"] = {
        "present": True,
        "entries": len(manifest),
        "verified": not mismatches,
        "mismatches": mismatches,
    }


def native_board_summary(package: Path, failures: list[str]):
    board_path = package / "source" / "oscillator.kicad_pcb"
    if not board_path.is_file():
        failures.append("Native board is missing from the review package")
        return None
    completed = subprocess.run(
        [str(KICAD_PYTHON), str(HERE / "native_board_summary.py"), str(board_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode:
        failures.append(f"Native KiCad board inspection failed: {completed.stderr.strip()}")
        return None
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        failures.append(f"Native KiCad board inspection returned invalid JSON: {exc}")
        return None


def drill_summary(layer):
    if layer is None:
        return None
    drill_count = sum(1 for _ in layer.drills())
    slots = list(layer.slots())
    tools = []
    for tool, count in sorted(
        layer.hit_count().items(), key=lambda item: item[0].equivalent_width(MM)
    ):
        width = tool.equivalent_width(MM)
        tool_slots = [obj for obj in slots if obj.tool == tool]
        tools.append(
            {
                "diameter_or_width_mm": width,
                "objects": count,
                "drills": count - len(tool_slots),
                "slots": len(tool_slots),
                "slot_cut_lengths_mm": [obj.curve_length(MM) for obj in tool_slots],
            }
        )
    path = Path(layer.original_path) if layer.original_path else None
    return {
        "file": layer.original_path.name if layer.original_path else None,
        "plating_interpretation": layer.plating_type,
        "x2_file_function": drill_file_function(path) if path else None,
        "drills": drill_count,
        "slots": len(slots),
        "objects": len(layer.objects),
        "bounds": bounds_dict(layer.bounding_box(MM)),
        "tools": tools,
    }


def markdown_report(result: dict) -> str:
    lines = [
        "# Independent fabrication export inspection",
        "",
        f"Candidate: `{result['package']}`  ",
        f"Inspected UTC: {result['inspected_utc']}  ",
        f"Parser: Gerbonara {result['parser_version']}  ",
        f"Automated result: **{result['automated_result']}**",
        "",
        "This is an internal review result, not a manufacturing release or order approval.",
        "",
        "## Package and geometry",
        "",
        f"- Manifest verified: `{result['manifest'].get('verified', False)}`",
        f"- Generator classified by parser: `{result.get('generator')}`",
        f"- Board name: `{result.get('board_name')}`",
        f"- Board bounds: `{result.get('board_bounds')}`",
        f"- Outline centerline bounds: `{result.get('outline_centerline_bounds')}`",
        f"- Closed outline polygons found: `{result.get('outline_polygon_count')}`",
        "",
        "## Layer map",
        "",
        "| Layer | File | X2 FileFunction | Bounds (mm) | Within outline range |",
        "|---|---|---|---|---|",
    ]
    for layer in result["layers"]:
        lines.append(
            f"| {layer['role']} | `{layer['file']}` | `{layer['x2_file_function']}` | "
            f"`{layer['bounds']}` | `{layer['within_outline_range']}` |"
        )

    lines.extend(["", "## Drills and routed slots", ""])
    for label in ("pth", "npth"):
        drill = result["drills"].get(label)
        if drill is None:
            lines.append(f"- {label.upper()}: missing")
            continue
        lines.append(
            f"- {label.upper()} `{drill['file']}`: {drill['drills']} drilled holes, "
            f"{drill['slots']} routed slots, bounds `{drill['bounds']}`, "
            f"within outline range `{drill['within_outline_range']}`."
        )
        for tool in drill["tools"]:
            slot_lengths = ", ".join(f"{x:.3f}" for x in tool["slot_cut_lengths_mm"]) or "-"
            lines.append(
                f"  - {tool['diameter_or_width_mm']:.3f} mm tool: "
                f"{tool['drills']} drills, {tool['slots']} slots; slot cut lengths mm: {slot_lengths}"
            )

    native = result.get("native_board")
    lines.extend(["", "## Native-board cross-check", ""])
    if native:
        lines.append(
            f"- Source SHA-256 `{native['sha256']}`; {native['footprints']} footprints "
            f"({native['electrical_footprints']} electrical + {native['npth_mount_footprints']} NPTH mounts), "
            f"{native['segments']} track segments, and {native['vias']} vias."
        )
        lines.append(
            f"- Native drilled features: {native['pth_round_pads']} round PTH pads, "
            f"{native['pth_slots']} PTH slots, {native['npth_pads']} NPTH pads, plus {native['vias']} vias."
        )
        lines.append(f"- Native drill sizes: `{native['pad_drill_sizes_mm']}`")

    lines.extend(["", "## Automated findings", ""])
    if result["failures"]:
        lines.extend(f"- FAIL: {item}" for item in result["failures"])
    else:
        lines.append("- No automated package-structure, parse, extent, or drill-separation failure was found.")
    lines.extend(f"- NOTE: {item}" for item in result["notes"])

    lines.extend(
        [
            "",
            "## Manual release gates still required",
            "",
            "- Open `top.svg`, `bottom.svg`, and `all-layers.svg` and visually verify drill-to-pad registration, "
            "mask-to-copper registration, outline closure, readable legend, and absence of mirrored or shifted data.",
            "- Confirm every routed slot has the intended width, length, plating, and component association against "
            "the approved footprint drawings; automated counts do not establish mechanical fit.",
            "- Compare the board dimensions and drill table with the routed native board and the selected supplier limits.",
            "- Confirm the DRC/ERC reports and all gates in `fabrication/manufacturing-checklist.md` before release.",
            "- Any source or export correction requires a new immutable review-package revision and a fresh inspection.",
            "",
        ]
    )
    return "\n".join(lines)


def inspect(package: Path, output: Path) -> dict:
    package = package.resolve()
    if not package.is_dir():
        raise SystemExit(f"Review package directory does not exist: {package}")
    gerbers = package / "gerbers"
    if not gerbers.is_dir():
        raise SystemExit(f"Gerber directory is missing: {gerbers}")
    if output.exists():
        raise SystemExit(f"Refusing to overwrite an existing inspection result: {output}")

    failures: list[str] = []
    notes: list[str] = []
    result = {
        "package": str(package),
        "inspected_utc": datetime.now(timezone.utc).isoformat(),
        "parser_version": gerbonara.__version__,
        "failures": failures,
        "notes": notes,
    }
    verify_manifest(package, failures, result)
    native = native_board_summary(package, failures)
    result["native_board"] = native
    if native:
        provenance_path = package / "source-provenance.json"
        try:
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            expected_hash = provenance.get("pcb\\oscillator.kicad_pcb")
            if native["sha256"] != expected_hash:
                failures.append(
                    f"Native source hash {native['sha256']} differs from provenance {expected_hash}"
                )
        except (OSError, json.JSONDecodeError) as exc:
            failures.append(f"Source provenance cannot be parsed: {exc}")
        expected_native = {
            "footprints": 81,
            "electrical_footprints": 77,
            "npth_mount_footprints": 4,
            "segments": 591,
            "vias": 39,
        }
        for key, expected in expected_native.items():
            if native[key] != expected:
                failures.append(f"Native {key} is {native[key]}, expected {expected}")
        if not (
            abs(native["edge_bbox_width_mm"] - 95.05) <= 0.01
            and abs(native["edge_bbox_height_mm"] - 79.05) <= 0.01
        ):
            failures.append(
                "Native board edge stroke bounding box is not 95.050 x 79.050 mm: "
                f"{native['edge_bbox_width_mm']:.3f} x {native['edge_bbox_height_mm']:.3f} mm"
            )

    stack = LayerStack.open(gerbers)
    result["generator"] = stack.generator
    result["board_name"] = stack.board_name

    actual_layers = set(stack.graphic_layers)
    missing = sorted(REQUIRED_LAYERS - actual_layers)
    unexpected = sorted(actual_layers - REQUIRED_LAYERS)
    if missing:
        failures.append(f"Required Gerber layers missing: {missing}")
    if unexpected:
        failures.append(f"Unexpected or erroneous Gerber layers present: {unexpected}")

    recognized_files = set()
    layer_rows = []
    board_bounds = stack.board_bounds(MM, default=None)
    result["board_bounds"] = bounds_dict(board_bounds)
    if board_bounds is None:
        failures.append("A usable board outline/bounds could not be derived")

    try:
        polygons = list(stack.outline_polygons(unit=MM))
        result["outline_polygon_count"] = len(polygons)
        if len(polygons) != 1:
            failures.append(f"Expected one closed board outline polygon, found {len(polygons)}")
        elif polygons[0]:
            xs = [coordinate for primitive in polygons[0] for coordinate in (primitive.x1, primitive.x2)]
            ys = [coordinate for primitive in polygons[0] for coordinate in (primitive.y1, primitive.y2)]
            centerline_bounds = ((min(xs), min(ys)), (max(xs), max(ys)))
            result["outline_centerline_bounds"] = bounds_dict(centerline_bounds)
            width = result["outline_centerline_bounds"]["width_mm"]
            height = result["outline_centerline_bounds"]["height_mm"]
            if not (abs(width - 95.0) <= 0.01 and abs(height - 79.0) <= 0.01):
                failures.append(f"Outline centerline is {width:.3f} x {height:.3f} mm, expected 95.000 x 79.000 mm")
    except Exception as exc:  # parser supplies useful topology errors
        result["outline_polygon_count"] = 0
        failures.append(f"Board outline is not a single parseable closed contour: {exc}")

    for key in sorted(actual_layers):
        layer = stack.graphic_layers[key]
        file_path = Path(layer.original_path) if layer.original_path else None
        if file_path:
            recognized_files.add(file_path.resolve())
        layer_bounds = layer.bounding_box(MM)
        file_function = gerber_file_function(file_path) if file_path else None
        expected_function = EXPECTED_FILE_FUNCTIONS.get(key)
        if key != ("mechanical", "outline"):
            if not file_function:
                failures.append(f"{key} lacks an X2 TF.FileFunction attribute")
            elif expected_function and tuple(file_function[: len(expected_function)]) != expected_function:
                failures.append(
                    f"{key} has X2 FileFunction {file_function}, expected prefix {expected_function}"
                )
        elif not file_function or file_function[0] != "Profile":
            failures.append(f"Outline has X2 FileFunction {file_function}, expected Profile")

        inside = contains(board_bounds, layer_bounds)
        if key != ("mechanical", "outline") and inside is False:
            failures.append(f"{key} plotted extent exceeds the outline range by more than 0.15 mm")
        layer_rows.append(
            {
                "role": " ".join(key),
                "file": file_path.name if file_path else None,
                "x2_file_function": file_function,
                "bounds": bounds_dict(layer_bounds),
                "within_outline_range": inside,
            }
        )
    result["layers"] = layer_rows

    pth = drill_summary(stack.drill_pth)
    npth = drill_summary(stack.drill_npth)
    result["drills"] = {"pth": pth, "npth": npth}
    for label, source, summary in (("PTH", stack.drill_pth, pth), ("NPTH", stack.drill_npth, npth)):
        if source is None or summary is None:
            failures.append(f"Separate {label} drill file is missing")
            continue
        if source.original_path:
            recognized_files.add(Path(source.original_path).resolve())
        summary["within_outline_range"] = contains(
            board_bounds,
            source.bounding_box(MM),
            tolerance_mm=0.15,
        )
        if summary["within_outline_range"] is False:
            failures.append(f"{label} drill/slot extent exceeds the outline range by more than 0.15 mm")
        if summary["objects"] == 0:
            failures.append(f"Separate {label} drill file contains no drill or slot objects")
        expected_drill_function = "Plated" if label == "PTH" else "NonPlated"
        declared = summary["x2_file_function"]
        if not declared or declared[0] != expected_drill_function or declared[-1] != label:
            failures.append(
                f"{label} drill X2 FileFunction is {declared}, expected {expected_drill_function},...,{label}"
            )

    if stack._drill_layers:
        extras = [layer.original_path.name for layer in stack._drill_layers]
        failures.append(f"Unclassified or mixed drill files present: {extras}")
        for layer in stack._drill_layers:
            if layer.original_path:
                recognized_files.add(Path(layer.original_path).resolve())

    if pth is not None and pth["slots"] == 0:
        failures.append("No routed PTH slots were found; the Alps retention-slot export is expected")
    if native and pth and npth:
        if pth["drills"] != native["pth_round_pads"] + native["vias"]:
            failures.append("PTH circular-drill count differs from native round pads plus vias")
        if pth["slots"] != native["pth_slots"]:
            failures.append("PTH routed-slot count differs from native oblong-pad count")
        if npth["drills"] != native["npth_pads"] or npth["slots"] != 0:
            failures.append("NPTH drill/slot count differs from native NPTH pads")

    job_files = list(gerbers.glob("*.gbrjob"))
    if len(job_files) != 1:
        failures.append(f"Expected one Gerber job file, found {len(job_files)}")
    else:
        job_path = job_files[0]
        recognized_files.add(job_path.resolve())
        try:
            job = json.loads(job_path.read_text(encoding="utf-8"))
            attrs = job.get("FilesAttributes", [])
            listed = {entry.get("Path") for entry in attrs}
            plotted = {
                Path(layer.original_path).name
                for layer in stack.graphic_layers.values()
                if layer.original_path
            }
            if listed != plotted:
                failures.append(
                    f"Gerber job layer list differs from parsed plotted layers: listed={sorted(listed)}, parsed={sorted(plotted)}"
                )
            if job.get("GeneralSpecs", {}).get("LayerNumber") != 2:
                failures.append("Gerber job does not declare a two-layer board")
            general = job.get("GeneralSpecs", {})
            project_id = general.get("ProjectId", {})
            if project_id.get("Revision") != "R1":
                failures.append(
                    f"Gerber job revision is {project_id.get('Revision')!r}, expected 'R1'"
                )
            if general.get("Finish") != "ENIG":
                failures.append(
                    f"Gerber job finish is {general.get('Finish')!r}, expected 'ENIG'"
                )
            if abs(float(general.get("BoardThickness", 0)) - 1.6) > 0.001:
                failures.append("Gerber job board thickness is not 1.600 mm")
            job_size = general.get("Size", {})
            if not (
                abs(float(job_size.get("X", 0)) - 95.05) <= 0.01
                and abs(float(job_size.get("Y", 0)) - 79.05) <= 0.01
            ):
                failures.append("Gerber job plotted size is not 95.050 x 79.050 mm")
            result["gerber_job"] = {
                "file": job_path.name,
                "generation_software": job.get("Header", {}).get("GenerationSoftware"),
                "creation_date": job.get("Header", {}).get("CreationDate"),
                "general_specs": job.get("GeneralSpecs"),
                "listed_plot_files": sorted(listed),
            }
        except (OSError, json.JSONDecodeError) as exc:
            failures.append(f"Gerber job file cannot be parsed: {exc}")

    all_files = {path.resolve() for path in gerbers.rglob("*") if path.is_file()}
    unknown_files = sorted(str(path.relative_to(gerbers.resolve())) for path in all_files - recognized_files)
    if unknown_files:
        failures.append(f"Unrecognized files in Gerber directory: {unknown_files}")
    result["gerber_directory_files"] = sorted(str(path.relative_to(gerbers.resolve())) for path in all_files)
    result["unrecognized_files"] = unknown_files

    notes.append(
        "Extent containment is a range check only; inspect the generated overlays for true registration and polarity."
    )
    notes.append(
        "Gerber positive/negative image semantics are parser-rendered; solder-mask openings must be checked visually."
    )

    result["automated_result"] = "FAIL" if failures else "PASS (manual gates pending)"
    output.mkdir(parents=True)
    bounds = board_bounds or stack.bounding_box(MM, default=((0, 0), (0, 0)))
    side_common = {
        "mechanical outline": "#ff00ff",
        "drill pth": "#00ffff",
        "drill npth": "#ff8800",
        "drill unknown": "#ff0000",
    }
    top_colors = {
        **side_common,
        "top copper": "#cc0000dd",
        "top mask": "#00aa0088",
        "top silk": "#ffffff",
    }
    bottom_colors = {
        **side_common,
        "bottom copper": "#0044ccdd",
        "bottom mask": "#00aa0088",
        "bottom silk": "#ffffff",
    }
    (output / "top.svg").write_text(
        str(stack.to_svg(margin=2, side_re="top|mechanical", force_bounds=bounds, colors=top_colors)),
        encoding="utf-8",
    )
    (output / "bottom.svg").write_text(
        str(stack.to_svg(margin=2, side_re="bottom|mechanical", force_bounds=bounds, colors=bottom_colors)),
        encoding="utf-8",
    )
    colors = {
            "top copper": "#cc0000aa",
            "bottom copper": "#0044cc88",
            "top mask": "#00aa0066",
            "bottom mask": "#00aa0066",
            "top silk": "#ffffff",
            "bottom silk": "#dddddd",
            "mechanical outline": "#ff00ff",
            "drill pth": "#000000",
            "drill npth": "#ff8800",
            "drill unknown": "#ff0000",
        }
    (output / "all-layers.svg").write_text(
        str(stack.to_svg(margin=2, force_bounds=bounds, colors=colors)), encoding="utf-8"
    )
    try:
        import cairosvg

        for name in ("top", "bottom", "all-layers"):
            cairosvg.svg2png(
                url=str(output / f"{name}.svg"),
                write_to=str(output / f"{name}.png"),
                output_width=1900,
            )
    except ImportError:
        notes.append("CairoSVG is unavailable; SVG views were created without PNG copies.")
    (output / "inspection.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (output / "inspection.md").write_text(markdown_report(result), encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path, help="immutable review-package revision directory")
    parser.add_argument(
        "--output",
        type=Path,
        help="new output directory; default is fabrication/inspection/results/<revision>",
    )
    args = parser.parse_args()
    output = args.output or HERE / "results" / args.package.name
    result = inspect(args.package, output.resolve())
    print(json.dumps({"result": result["automated_result"], "output": str(output.resolve())}, indent=2))
    raise SystemExit(1 if result["failures"] else 0)


if __name__ == "__main__":
    main()
