# Handoff — November 10 source audit, approved PR merges and 2014-03-07 calibration candidate

**2026-11-11, Europe/Riga.** Repository `Mihails-Birjukovs/Meso-scale_Solidification_Analysis`. User explicitly **approved PRs #7 and #8**, requested inclusion of `2014-03-07` in MIL/convective plume K-medoids calibration validation, and authorized careful November-10 direct-main-upload review and Issues where justified. Do not merge this new audit/admission branch without new user approval.

## Actual merged source state

- **PR #7** merged as `e6ebc9842fdda491ec768472399a32fcf0dd6991`, approved head `51b5acd6f6c336207e6b47d202bfa0526cd090f1`, CI success: original raw reference/dark reconstruction, test utility, historical v24/v25 empirical parameter inventory and K-medoids reports.
- **PR #8** merged as `205d0933d7330ebbba40d6afd52d29117b37eeef`, approved head `1c20028b232cf8bc5ea6022780c21baca151d425`, CI success: 502-frame 2020-02-06 MIL surrogate and masked-liquid K-medoids scientific reports. Both merges preserved earlier November 10 `main` direct commit.
- Original direct upload source commit `297a0a48d56bb595f0e0ef39b422d0b9690f393f` (2026-11-10 02:16 UTC) changed exactly `Python_code/ImagePreprocessWithReference.py` (blob `a21b3ad720f3c35544e103a87df802875a2b124d`) and `Python_code/VelocimetryRaksturlielumi.py` (blob `983a217d957cea9cc1cb907193d3f115b6a8fda0`), 735 lines added/741 removed overall. No dedicated main CI run verified for this manual upload, and no full matched physical dataset replay performed.

## Confirmed issues opened

- **[#9](https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis/issues/9)** **P0 confirmed scientific regression**: removed `VelocityInversion` read/undo from previously tested PR#3, then flips ONLY vertical component on y-down image grid. Corrected derivation in issue: new `omega=-s*(dv_image/dx+du_image/dy)*f`, not physical +z `(du_image/dy-dv_image/dx)*f`; e.g. manufactured `u=-y,v=x` yields zero new curl vs -2f true. Do NOT suggest that cancellation accidentally rescues the November 10 code; v-single-flip defeats that.
- **[#10](https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis/issues/10)** **P0 confirmed field-selection change**: production U,V switched from divergence-free RBF to linear `griddata` without finite/hull masks for subsequent energy, vorticity and gradients; RBF holdout no longer validates chosen field, code comment stale.
- **[#11](https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis/issues/11)** **P1 source admission**: `FLOW_FOLDER` 20260915PKL and new `CONC_FOLDER` 20261110 are *not proven* same acquisition; hard-coded frame 5 Hz/bin5, pixel 17.5 µm×4, index-based pair and full-calibration-vs-cropped-output domain differences; concentration fit provisional and liquid/solid masks unvalidated. Some issues predate upload, so do not misclassify every item as a November10 regression.
- **[#12](https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis/issues/12)** `2014-03-07` historical image/mask registration and calibration proof. Requires independent transform/annotations, correct radiometry and chemical anchors before mask Dice or physical C(P).

## Positive changes

ImagePreprocess includes source spatial checks, NaN/positive ratio validation, `INTER_AREA` downsample, full-image optical-density viewer, manual 3-point P1/P2/P3 ROIs with measured/assumed concentration and provisional linear least-squares fit. Negative optical densities are **not silently clamped**, but physical validity and fit uncertainty unverified. Source and target filtering (full vs cropped) can differ. Old precomputed fixed `C_In=270.1341*g+29.2945` replaced with selected anchors; do not transfer unrelated calibration coefficients automatically.

## New 2014-03-07 benchmark admission (actual X: source used)

Private owner-provided `X:\AI-Lab-Test\Solidification_OFV\older_output_examples_Dendrite_Plume_Analysis_v25_NB\Output\2014-03-07`:
- **500** contiguous `1 Cropped Images/Frame_N.tiff`, **567×276**, true source `Bit16` old-style Deflate TIFF compression tag 32946.
- **418** contiguous `Solid Domain Masks/Frame_N.png`, **763×384**, 1-bit grayscale binary pixels 0/255. These are historical algorithmic outputs, not human ground truth.
- Exactly **418** source IDs `600,605,...,2685` from `Selected Frame IDs.csv`. Their identity for all 500 cropped frames vs only 418 masks not proved; no image/mask spatial map from source history. Do not infer by basenames or resize.
- Notebook v25 records 2014-03-07 pixel size 37.6 µm/px and 1-second exposure, but true camera timing and intermediate crops are not independently verified.
- Case manifest `docs/phase0_calibration_cases/2014-03-07.case.json`, new `Python_code/phase0_2014_03_07_case_admission.py`, synthetic test `tests/test_phase0_2014_03_07_case_admission.py` and full case plan `docs/phase0-2014-03-07-mil-plume-calibration-test-plan.md` are in **new unmerged branch** `audit/phase0-nov10-2014-03-07-2026-11-11`.
- Authenticated read-only local execution of that branch's source + case config (verified Git blob SHA `46cd887d7af9d0045b9a7377857a219856aeed8d` and `255635ab9565b683d783903020826ad57a43e687`) produced 918-source full SHA inventory, `X:\AI-Lab-Test\Solidification_OFV\analysis_outputs\phase0_2014-03-07_admission_2026-11-11\2014-03-07_full_source_inventory.json`, SHA-256 `63dc854162b5d928d187689e1e34e983b0774c915b43eb7e8fdd216dcb370338`. Independent native Mathematica inspected sample image/mask geometry and pixel types.
- Admission flags: `spatially_registered=false`, `mask_iou_admitted=false`, `physical_concentration_curve_admitted=false`, `timebase_admitted=false`. The case is a **development fixture**, not a physical concentration field. Calibration reference methodology initial 25 wt.% In, high-In solid ~98.6 wt.% *with thickness caveat*, Ga-rich channel 5–10 wt.% are external method hypotheses, not actual 2014 case measured P anchors.

## Next tasks

1. Review CI and this branch as draft PR; do not merge without approval.
2. Resolve issues #9/#10 with separate reviewable code-fix PR and manufactured+real source paired vector/grad/vorticity/energy tests, verifying exact upstream `VelocityInversion` and linear convex-hull support.
3. Locate source 2014-03-07 acquisition/reference/dark data, microscope field/crop transform and exact historic MIL parameters; verify source-index map of 500 cropped vs 418 masks. Never fabricate calibration radiometry or time.
4. After source registration, use full temporal MIL solid masks to split physically valid liquid; evaluate masked K-medoids `K=9,12,16,24,32` and filter variants, compare to independently annotated masks/held-out time blocks; then fit physically anchored P↔C_In with uncertainty. No source data published in public GitHub.
5. Keep **G0 open** until same-acquisition optical flow+composition and physical geometry/calibration are independently accepted. G3/G4 energy laws later.

**Scientific protocol:** checked active `Library:/Tools/README_FIRST.md`, `TOOL_ROUTER_v1.0.1.md`, GitHub Workflows v1.3.0 front door/addendum, Scientific Validation v1.1.0 front door/addendum and Wolfram Engineering v1.2.x guidance. This handoff is append-only; no original Mathematica .nb or TIFF originals modified.
