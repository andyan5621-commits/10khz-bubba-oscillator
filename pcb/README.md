# PCB revision — planned

No PCB has been designed, fabricated, or measured in this repository yet. The
breadboard is the measured baseline. Add the selected EDA project when work starts.

| Folder | Intended contents |
|---|---|
| `design/` | Native EDA schematic, PCB layout, project, and project-local libraries |
| `fabrication/` | Revision-tagged Gerbers, drill files, board outline, fabrication notes |
| `assembly/` | Revision-tagged BOM, placement files, assembly drawings and photos |
| `validation/` | Bring-up notes, oscilloscope/FFT captures and PCB performance results |

## Development checklist

- [ ] Capture and check the breadboard-equivalent schematic.
- [ ] Decide how to handle output loading, amplitude control and frequency trim.
- [ ] Plan grounding, short sensitive connections and local supply decoupling.
- [ ] Run the EDA tool's electrical and layout checks.
- [ ] Save a tagged design revision before releasing manufacturing files.
- [ ] Assemble and test the supply rails and individual stages.
- [ ] Repeat fixed-amplitude waveform and spectrum measurements.
- [ ] Compare PCB results with the archived breadboard baseline.

Record any circuit changes in the same commit as the changed schematic/layout.
Keep generated manufacturing releases grouped by board revision. Report new PCB
measurements separately from the existing breadboard results.
