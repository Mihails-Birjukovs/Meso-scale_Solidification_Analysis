# Handoff — original raw reference/dark means, v25 metadata and K-medoids level sweep

**Date:** 2026-11-02, Europe/Riga. **Repo:** `Mihails-Birjukovs/Meso-scale_Solidification_Analysis`. **Parent:** user-approved PR #6, merged `cc5120223777ce675ee2ee1c62a6c9b2f779e8e6`. **Branch:** `feat/phase0-reference-stacks-kmedoids-2026-11-02`; requires owner review, not merged.

## User decisions recorded
1. Approves reconstructing **per-pixel mean reference and mean dark TIFFs from all original available beam/reference and dark TIFF exposures**, and preserving no-dark correction branch.
2. Calls for using notebook v25's **liquid plume K-medoids** as a candidate automatic region proposal. Prefer solid segmentation and physically admissible liquid mask **before** intensity clustering; if unmasked, test **more K levels** to account for solid/background but do not assume bigger K is always better.
3. Notes original notebook contains per-sequence frame rate/exposure and pixel size metadata, which has now been verified.

## Confirmed source notebook metadata
Exact original notebook (814430 B; Git blob SHA b13ef6adda22405d89680e3ebe5da50e6f40d297) Import Images Abstract lists:
- 2014-04-04, 2014-03-07: 37.6 µm/pixel;
- 2011-09-19-Exp2: 23.7 µm/pixel;
- 2014-04-15-Exp2: 17.3 µm/pixel;
- 2011-09-09 Exp1 and Exp2: 17.5 µm/pixel;
- 2020-02-03: 11 µm/pixel; 2020-02-06 and 2020-02-10: 17.5 µm/pixel.
It states exposure time **1 s in all listed cases**; active 2011-09-09 Exp1 Input sets `pixelSizeMuMeters=17.5` and `frameDurationSeconds=1`. This is source notebook metadata, NOT independent camera log or verified mapping to later binning/OFV.

## Original detector-stack reconstructions, locally generated and Mathematica-checked

`X:\AI-Lab-Test\Solidification_OFV\analysis_outputs\phase0_scout_2026-11-01\`

- `reconstructed_2014-01-15`: 113 reference and 105 dark exposures (all uint16 TIFFs). Per-pixel arithmetic mean detector counts R=58230.418, D=55592.473, R>D for 72.30% of pixels. Mean *per-frame means* R range 58192.13–58270.35, D range 54041.20–56334.98.
- `reconstructed_2014-04-15-Exp2`: 108 reference and 120 dark exposures. R=57847.084, D=54317.608, R>D for 77.22% of pixels. Frame-mean R 57798.80–57881.69, D 51751.05–55532.51.
- All arithmetic accumulation done float64; exported 32-bit float grayscale TIFF mean R, mean D, mean R−D **with no rescaling or clipping**; individual TIFF SHA-256/per-frame metadata kept in JSON. Mathematica 12.1 independently imported TIFFs and verified dimensions and numerical means. Originals unchanged; selected individual raw TIFF *working copies* extracted only to X:. No raw data pushed to public repo.
- Compare the 2014-04-15 archived TIFFs labelled `Averaged`: average R means 28717.718, average D 28329.149, correlations with true raw-stack means **+0.00442** and **−0.00062**, respective RMSE ≈34465.59 and ≈31606.55 raw counts. Simple byte swap, unsigned inversion and signed interpretation do not reconcile. Do not assume corruption mechanism; this is **unverified processed-product provenance**. Single original reference/dark and average-based OD branches are dramatically different.
- Recomputed OD on 2014-04-15 first/last original experiment frames with full-stack means: full-image dark-valid fractions 0.7592 / 0.4688; ROI 200x200 0.9997 / 0.7443; full image median g reference-only +0.0008 / +0.0601, dark-corrected +0.0033 / +0.5990.
- For 2014-01-15 first/middle/last with full means, full dark-valid 0.7111 / 0.5922 / 0.4110; central patch 0.9999 / 0.9699 / 0.8819. Strict positivity, no clamped g, no composition conversion.
- Public generic reproducibility helper in this branch `Python_code/phase0_reference_dark_reconstruction.py` and its synthetic tests; check repo CI. Generic source helper ought to be rerun against X: original images and compared to initial notebook/stdlib reconstructions before claiming full cross-script equivalence.

## Actual K-medoids sensitivity experiment
Local `kmedoids_level_sweep_2014-01-15` holds 12 PNG images, 1 mask and detailed JSON + original WolframScript. Middle 2014-01-15 original experimental 760x560 uint16 frame; central 200x200 ROI; branches g ref-only/dark-corrected; levels K=9,16,24; filters none or 1-pixel Gaussian. All 12 classifications had **exactly K nonempty labels**. Dark corrected OD valid 38797/40000 (96.99%). Preprocessing only on segmentation display copies: 1%-99% per-branch OD range and Gaussian filtering; quantitative g preserved. **No physical solid mask, manual plume label, ground-truth class/chemistry or full notebook temporal mask was used.** Unmasked invalid pixels replaced by zero inside segmentation view, so one cannot interpret K levels as chemical composition. Higher-K feasibility shown, optimal level count unproven.

## Reproducibility, G0 gates and next steps
Full written analysis: `docs/phase0-reconstructed-backgrounds-and-kmedoids-2026-11-02.md`. Compare 2014 background detector stability and original processing/averaging history, certify physical cell mask, run full notebook MIL solid segmentation, then repeat K=9,12,16,24,32 masked/unmasked on matched temporal frames and annotate validation labels. Calibration inputs from Natalia Shevchenko: 25 wt% In at P=0; ~98.6% indium-rich dendrites conditional full-thickness; Ga-rich channel ~5–10 wt% In. Do not carry such region anchors across unrelated acquisitions. Same-acquisition raw→processed→OFV geometry and source clock still needed. **G0 NOT CLOSED**; later mechanical energy closure out of scope.
