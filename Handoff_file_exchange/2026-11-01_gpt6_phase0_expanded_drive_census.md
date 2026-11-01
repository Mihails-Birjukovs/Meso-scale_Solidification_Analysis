# Agent handoff — Expanded Drive dataset discovery and Oct-27 artifact audit

**Date:** 2026-11-01, Europe/Riga.  
**Agent:** ChatGPT GPT-6, Coding/Optimization/Docs — Ga–In OFV.  
**Base:** `main@80f9b28b59a6e15711e7f9c77723b6917121bce3`, PR #4 merged after explicit user approval.  
**Feature branch:** `docs/phase0-drive-census-2026-11-01` (documentation-only, awaiting review).  
**Instruction:** Append-only; all earlier handoffs remain intact.

## Explicit user decisions

1. Keep **image x-right/y-down** in the current reconstruction; use physically oriented +z curl and explicit Cartesian y-up integration where needed.
2. Implement OFV-pair-midpoint / calibrated-composition alignment separately; **never infer acquisition time from processed archive names**.
3. User authorized exploration of other image sequences in Drive and, if needed, raw archives under `Raw Images for MSc`.

## Verified fresh discoveries

- [`2WCF-SVD -- Article / Image_sequences / Solidification`](https://drive.google.com/drive/folders/1CHVHJiz8jiAXjUvB6Kw5Sz2AiMZm5Cpi): 80×82×98, 100×68×170, 400×141×190 processed uint16 TIFF image stacks, archive directories and representative frame dimensions directly read.
- [`Image_sequences`](https://drive.google.com/drive/folders/1yP5XtRkbiq2SqR3qei45MbAFY8yb7G6R): unfiltered `optical_density`, TV-Gaussian and TV-Laplacian variants, all 301×106×69 TIFF frames. Filtered versions show corresponding image content in samples; they are not verified quantitative concentrations.
- [`Raw Images for MSc`](https://drive.google.com/drive/folders/1So6iAgNoLnmcELurrMFBTpYVvWVldLjP): three raw `.7z` archives sized 2.85 GB, 1.51 GB, 1.18 GB; attempting the smallest through the connected Drive interface returned explicit HTTP 413 at a **268,435,456 byte** transfer ceiling. No archive interior was accessed; no claim as to whether it has correct calibration, clock, geometry or matches any processed 2026 sequence.
- Newly found [`Kristofers PhD`](https://drive.google.com/drive/folders/1EaxfxxTnOqI_ukscr4Tfd3FqbsHH5FOP) contains `20261027.zip` and `20261027Nr2.zip` (~34.5 MB each). Both downloaded and inspected read-only: 20 fields of eight named NumPy arrays, 30×50 grids, plus saved summaries and plots. No raw/PKL/concentration TIFF/acquisition metadata manifest inside.
- **Exact internal consistency**: `kinetic_energy = 0.5*rho*speed²`, and `sum(E)*dV=E_total`, `sum(dissipation)*dV=dissipation_W`, for both 20-frame outputs to floating-point precision. The stored viscosity is the historical *mass-linear* law, not the approved two model sensitivity variants. The two output sets have bitwise equal density, mass fraction and viscosity, but substantially different derivative/flow data.
- Across all 20×30×50 cells, first versus Nr2: speed normalized RMSE 0.146, kinetic energy 0.321, vorticity 0.804, dissipation 0.985; these numbers **must not be attributed to a particular code edit or used for energy closure** without run configuration/provenance. The output CSV time axis 0–19s is not an independently verified camera time sequence.

## Full supporting audit

See [`docs/phase0-drive-dataset-census-2026-11-01.md`](../docs/phase0-drive-dataset-census-2026-11-01.md). It lists exact source folders, sample image shapes, archive admission results, array comparisons, uncertainty/normalization and recommended dataset choice.

## Decisions for next work

**G0 remains PARTIAL.** Do not force-align unrelated processed image shapes (82×98, 68×170, 141×190, 106×69, 90×150), treat filtered OD as untouched composition or promote an energy residual from old cropped-domain code to a physical balance. Recover the same-acquisition source/reference/calibration/clock/crop and `Conc_In`/PKL bundle for the promising 20-frame output first. If that fails, inspect the raw MSc archives via a small exported sample and archive listing in an environment without the large-download limit, avoiding unnecessary 1–3 GB transfers until experiment identity is established.

No source code, upstream repo or data archive was modified during this census. This handoff supplements rather than overwrites all existing repository handoffs.
