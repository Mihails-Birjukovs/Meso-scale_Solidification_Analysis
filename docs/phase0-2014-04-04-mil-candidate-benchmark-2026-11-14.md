# 2014-04-04: native v25 MIL-method and candidate mask benchmark

Date 2026-11-14. Original private Ga–In radiography archive SHA256: 77fac9a38a9cdaa41ee5ec9c9562acb7149ee1cee8f0246a80c2b267928f2510.

**Evidence stage: exploratory source-CRC-verified segmentation candidates, NOT original v25 solid-mask replay, independently verified phase labels, physical pixel calibration or C_In calibration.**

## Separate, source-faithful methods

The original v25 notebook (Git blob b13ef6adda22405d89680e3ebe5da50e6f40d297) defines flatFieldCorrect by ImageMultiply[image,flatField^-1] and its MIL series as Mean @ ColorNegate @ ImageAdjust @ GaussianFilter of the flat-corrected image. The full historical solid-mask method also uses **temporal MIL-dependent dynamic thresholding** and case-specific options. We have NOT reproduced that full temporal method. The historical v24 PDF 2020-02-06 thresholdFactor=17.5, dynamicThresholdBias=22.5 and dynamicThresholdPower=1 are case-specific empirical overrides; never assume they apply in 2014-04-04.

Two distinct quantities are available:

1. **Native v25 MIL-method samples:** licensed Windows Mathematica 12.1.1 evaluated the exact recovered formula on the same 21 source TIFFs using first-80-frame median measured-flat-field R80. GaussianKernelScale choices 0 and 1. The source-probe script is maintained in open draft PR #18; its associated per-21-frame source/config/result JSONs are private on X. No full native 3446-frame temporal MIL trace or historical dynamic threshold is yet accepted.
2. **Independent candidate image-change masks:** P_candidate=-ln(I_t/J0_candidate). J0_candidate is the first 80 contiguous original **main experimental sample** frames' pixelwise median; it is NOT the folder called Reference. The 111 Reference TIFFs are owner-confirmed **flat-field recordings** and provide a source-CRC-verified nonzero/nonsaturation detector mask. No dark correction is applied. Algebraically the same R cancels from (I/R)/(J0/R) in the flat-only branch, but an unknown additive detector offset and unverified specimen J0 mean that P_candidate is NOT accepted composition-relative physical attenuation.

All sampled TIFFs and baseline/reference source inputs were CRC32 checked against the SHA-verified original archive, preserving uint16 426x761 source pixels. Filename groups are derived by >1.5 s candidate timestamp gaps and by separate main/end roles; filename clock is not a certified camera clock.

## Deterministic sweep

Main original ordinals: 0,40,79,119,240,400,479,480,565,639,720,900,918,919,1200,1800,2600,3147. End ordinals: 0,150,297. Total 21 original frames.

- Unapproved candidate analysis rectangle in source detector coordinates: y=[120,412), x=[155,690). It is NOT physically accepted chamber/liquid geometry.
- Filters: none; Gaussian sigma=1px; Gaussian sigma=2px; median 3x3. Conservative invalid-neighbor checks prevent silent zero/saturation contamination.
- Fixed source-relative log thresholds: 0.02, 0.04, 0.08.
- Polarity: positive, negative, absolute (no inferred solid/liquid chemistry).
- Remove 4-connected components smaller than 25 pixels, retaining geometry and frame IDs.
- **21 x 4 x 3 x 3 = 756** parameter/frame/polarity rows. Record pixel support, candidate fraction, largest component, number of connected regions and bbox. Same-frame Jaccard describes *parameter sensitivity*, not mask accuracy. Empty-empty Jaccard is undefined, NOT perfect overlap.
- 18 individually SHA-recorded binary-mask review PNGs, plus source-image/contact sheet; all private.

## Representative results: Gaussian sigma 1, threshold 0.04

Fractions refer to valid pixels **inside the unapproved analysis rectangle**:

| Original source | Positive | Negative | Absolute |
|---|---:|---:|---:|
| main 119 | 0.00% | 0.00% | 0.00% |
| main 639 | 1.38% | 0.00% | 1.38% |
| main 1200 | 18.46% | 0.28% | 18.74% |
| main 3147 | 48.27% | 5.34% | 53.61% |
| end 297 | 71.37% | 5.33% | 76.70% |

The positive and negative maps show distinct, evolving image structures. **Positive fraction is not measured solid volume fraction; negative fraction is not chemically calibrated plume volume/5–10 wt% In**. Phase labels, physical ROI and camera time remain unapproved.

Main 1200 positive-mask same-filter Jaccard threshold 0.02 versus 0.04: 0.7211; threshold 0.04 versus 0.08: 0.1286; median3 versus Gaussian1 at threshold 0.04: 0.9008. Main 639 corresponding threshold Jaccards are 0.3524 and 0.0419. These reveal strong threshold sensitivity, particularly around onset.

**Controls:** exact unchanged synthetic specimen baseline produces zero detections under all parameters. Held-out 31 flat-field frames compared with first-80 flat-field median also produce zero detected components under the tested thresholds; early experimental frames are only *candidate* negatives, not independently proven pre-cooling truth. Synthetic 4px x-shift of a late original frame changes source-derived masks (positive Jaccard 0.6269, negative 0.1146): registration matters. This is NOT evidence of real instrument shift. None of these controls gives empirical false-positive rates against independent phase truth.

**Native Wolfram MIL method** on the 21 frames: sigma0 range 0.361659–0.474762 (median 0.437719), sigma1 range 0.353222–0.478887 (median 0.438399), inter-setting correlation 0.95612, maximum absolute difference 0.021208. The v25 temporal solid threshold remains to be reconstructed.

## X: source and artifact provenance

Private root: X:\AI-Lab-Test\Solidification_OFV\analysis_outputs\phase0_2014-04-04_mil_candidate_benchmark_2026-11-14

Authoritative results are in subfolder candidate_sweep_v2_conda:

| File | SHA256 |
|---|---|
| benchmark_manifest.json | 16167D36D71370B00484E66B142AAA03E5EABEE587B04C5D82A607E1EE37D2F1 |
| per_source_parameter_sweep.csv | 355A394B1AAF3A3257C1251D8AF41F0FDB01AC359EDA46A0AA3ED9D622EB45A0 |
| parameter_sensitivity.csv | 00BFE0A2011ADFEC557203AA09C79521F29CAF52C8C8C97CFC7DA30A0EE74733 |
| candidate_mask_contact_sheet.png | 71DB379D3D8489045C67F111338B400562E70BB7D9D9AB79B2F7E332D6CDB3A4 |
| parameter_sensitivity_review_v2.png | 6307ACEEDF5AF64E72ABA50B1424170EED96F9C88651ECC0BB23F74EA3745E52 |

Native v25 MIL outputs are in the parent root: native_v25_MIL_method_sigma0_21frames.json SHA 6AF6D34CCC29791FC5C9DEB51D5B2C8A46A299A42E9B1EAE64A4686E83656305, and sigma1_21frames.json SHA A7F1431D35F2E6A871D62614FA6FFB1DE3E828F7750D1C578B4A0A4244E3D0E3.

### Reproducibility caveats

Default workstation Python 3.10 includes SciPy 1.8.0 with NumPy 1.26.4: SciPy itself warns that this is **unsupported**. The initial run is retained under candidate_sweep_v1 only as an independent cross-check. The already-installed, unmodified C:\ProgramData\Miniconda3\python.exe has NumPy 1.26.4 / SciPy 1.13.1 and is the **authoritative scientific runtime**. Rerunning with it produced **byte-identical two numerical result CSVs and all 18 of 18 identical binary-mask SHA256 values**. PNG contact-sheet bytes differ with Matplotlib versions, not with mask data. The latest compatible-environment run is candidate_sweep_v2_conda, with source-derived temporal groups rather than hardcoded indices.

The first parameter-sensitivity plotting attempt produced **blank charts due to a selection bug**. That v1 plot is REJECTED and retained solely for audit. Corrected parameter_sensitivity_review_v2.png verifies **21 actual data points per plotted parameter trace**. No numerical table or binary mask was changed by the chart correction.

The companion source and tests in this PR can be run locally with the pinned image-analysis dependencies. On the authorized Miniconda Python **11/11 synthetic tests passed**, including unchanged-image null, polarity, connected-component exclusion, missing/invalid detector pixels, strict ROI and SHA/CRC rejection. Lightweight CI may skip optional scientific-dependency tests; a green CI alone is not native scientific validation.

All data in the original TIFF archive, the v25 notebook, raw masks and production OFV source are unchanged. No raw X: radiographs or binary masks are committed to GitHub.

## Next acceptance gate

Review the six representative original-source overlays (main 119,480,639,1200,3147; end 297) to identify independent actual chamber and solid boundaries, possible plume channels and camera/cooling chronology. Only then reconstruct full temporal MIL with source-correct filters and source-derived dynamic thresholds, test physically registered masks against independent manual annotations, and quantify false solid merges, missed fronts and boundary continuity. The 2014-03-07 image/mask registration and source-matched OFV PKLs remain separate unresolved G0 tasks.

This PR is **draft for review**, independent of unmerged PR #18 (native MIL probe) and #19 (flat-only radiometry policy). It should not be merged without user approval; temperature data are not needed for these exploratory mask tests, but physical G0 acceptance remains open.

## Prepared independent expert review (deliberately unfilled)

Two extra private files in the benchmark root are now available: EXPERT_REVIEW_2014-04-04_SOURCE_UNFILLED.csv (SHA256 B93F2A80BBAEBC5AC7DCD65FC4D3E689AF04D71C5E0671A468320DB135D6B8E5) and EXPERT_REVIEW_README_2014-04-04.md (SHA256 DEE3A0E2739AA9B9500573267F85EED8A588B25F53D055BE2D030EDF37AF09FD). Six rows are source-pinned to main 119/480/639/1200/3147 and end 297, with blank independent reviewer entries for real cell/wall ROI, initial all-liquid state, genuine solid and plume labels, user-supplied annotation-mask filenames, false detections/missed regions and uncertainty. These are NOT preapproved and remain private on X:.
