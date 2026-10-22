"""Emit native KiCad board facts for inspect_package.py.

Run only with KiCad's bundled Python, which supplies pcbnew.
"""

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import pcbnew

board_path = Path(sys.argv[1]).resolve()
board = pcbnew.LoadBoard(str(board_path))
footprints = list(board.GetFootprints())
pads = [pad for footprint in footprints for pad in footprint.Pads()]
drilled = [pad for pad in pads if pad.GetDrillSize().x or pad.GetDrillSize().y]
pth_pads = [pad for pad in drilled if pad.GetAttribute() != pcbnew.PAD_ATTRIB_NPTH]
npth_pads = [pad for pad in drilled if pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH]
pth_slots = [pad for pad in pth_pads if pad.GetDrillShape() == pcbnew.PAD_DRILL_SHAPE_OBLONG]
pth_round = [pad for pad in pth_pads if pad.GetDrillShape() != pcbnew.PAD_DRILL_SHAPE_OBLONG]
tracks = list(board.GetTracks())
vias = [track for track in tracks if isinstance(track, pcbnew.PCB_VIA)]
segments = [track for track in tracks if isinstance(track, pcbnew.PCB_TRACK) and not isinstance(track, pcbnew.PCB_VIA)]
mount_footprints = [
    footprint
    for footprint in footprints
    if list(footprint.Pads())
    and all(pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH for pad in footprint.Pads())
]
edge_box = board.GetBoardEdgesBoundingBox()


def size_key(pad):
    size = pad.GetDrillSize()
    return f"{size.x / 1e6:.3f}x{size.y / 1e6:.3f}"


print(
    json.dumps(
        {
            "board_file": str(board_path),
            "sha256": hashlib.sha256(board_path.read_bytes()).hexdigest(),
            "footprints": len(footprints),
            "electrical_footprints": len(footprints) - len(mount_footprints),
            "npth_mount_footprints": len(mount_footprints),
            "segments": len(segments),
            "vias": len(vias),
            "pads": len(pads),
            "pth_round_pads": len(pth_round),
            "pth_slots": len(pth_slots),
            "npth_pads": len(npth_pads),
            "pad_drill_sizes_mm": dict(sorted(Counter(size_key(pad) for pad in drilled).items())),
            "edge_bbox_width_mm": edge_box.GetWidth() / 1e6,
            "edge_bbox_height_mm": edge_box.GetHeight() / 1e6,
        },
        indent=2,
    )
)
