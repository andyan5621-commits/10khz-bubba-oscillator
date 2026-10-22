# Independent Gerber and drill inspection

This folder provides an inspection path independent of KiCad's plotter. It uses
Gerbonara 1.6.3 installed under `vendor/`; no global Python environment was
changed. The inspection is read-only with respect to immutable review packages.

After `fabrication/package_review.py` creates a routed candidate, run:

```powershell
& 'C:\PythonSolvers\.venv\Scripts\python.exe' fabrication\inspection\inspect_package.py `
  fabrication\review-packages\<revision>
```

The command refuses to overwrite an existing result. Results are written under
`fabrication/inspection/results/<revision>/` and include:

- `inspection.json`: machine-readable layer, bounds, drill, slot, and finding data;
- `inspection.md`: review record and remaining manual gates;
- `top.svg`/`.png` and `bottom.svg`/`.png`: color-separated side views;
- `all-layers.svg`/`.png`: alignment overlay for copper, mask, legend, outline, PTH, and NPTH.

The automated checks verify the immutable-package hash manifest, the intended
seven-layer map, X2 file-function attributes, separate plated/non-plated drill
files, drill and routed-slot counts, a single closed outline, extents, and the
absence of unclassified files. Extent checks cannot prove registration or mask
polarity. A reviewer must inspect all three SVGs and compare the drill table and
dimensions against the approved native board, footprint drawings, supplier
rules, DRC/ERC reports, and manufacturing checklist.

Any correction to a board or export requires a new review-package revision and
a new inspection result. Nothing in this folder authorizes upload, release,
purchase, or assembly.
