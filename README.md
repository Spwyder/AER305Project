# Wing Spar Design Evaluator

`evaluation.py` analyzes a wing-spar design: shear and bending, factor of safety vs. engine placement, deflections, weight/cost and stringer buckling. It produces a one-page report sheet.

## Run a design on the website (no install needed)

Open the GitHub Pages site for this repo (anyone with the link can use it; no GitHub account needed), then either:

- **upload a design file** (drag it onto the page), or
- **pick one of the designs already in `designs/`** from the dropdown.

The page runs the repo's current `evaluation.py` with that design **inside your browser** (Python via [Pyodide](https://pyodide.org)) and shows the report sheet, which you can download as a PNG. The first run takes ~10–20 s while Python loads; later runs take a few seconds.

Uploaded files are not saved anywhere. To add a design to the dropdown, the repo owner puts it in `designs/` (on GitHub: open `designs/` → **Add file → Upload files** → commit).

## What a design file is

A design file contains **only the design block**: the lines that go between the two `#=====` lines under `#design parameters to change!` in `evaluation.py`. See `designs/` for examples and `spar_designs.md` for the design definitions.

It must define: `rhoSpar, E, stressYield, pricePerPound, strDistances, nStringers, strA, strI, strIt, ribLocations, ribsWeight, I, It, h, ht, area`. It can use `np`, `chord(x)`, `lWing`, `halfSpan` and anything else defined above the block.

## Run locally

Requires Python with numpy ≥ 2.0, scipy and matplotlib.

```bash
python evaluation_from_file.py designs/D2T_134ribs.py D2T_134ribs_report.png
```

`evaluation_from_file.py` is a copy of `evaluation.py` that reads the design block from a file. If `evaluation.py` changes outside the design block, regenerate it (the website doesn't depend on it: the site always uses `evaluation.py` directly).

## Updating the analysis

Edit/upload `evaluation.py` and push. The website picks it up automatically (it shows the first 12 characters of the SHA-256 of the `evaluation.py` it ran, so you can confirm which version was used). Keep the `#design parameters to change!` line followed by the two `#=====` marker lines: the site uses them to find the design block.

## Repo layout

| Path | What |
|---|---|
| `evaluation.py` | The analysis script (source of truth) |
| `evaluation_from_file.py` | Same script, design block read from a file |
| `designs/` | Design files (design block only) |
| `results/` | Report sheets generated for each design |
| `spar_designs.md` | Design definitions and expected section properties |
| `index.html`, `web/` | The website (`web/runner.py` swaps the design block in and runs the script) |
