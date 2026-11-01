# Historical v24 notebook MIL/plume parameter provenance: new example corpus

**Date:** 2026-11-02, Europe/Riga. **Status:** Documentation and research-data admission only. Owner supplied a new private X: folder `X:\AI-Lab-Test\Solidification_OFV\older_output_examples_Dendrite_Plume_Analysis_v25_NB` expressly to support empirical MIL segmentation and liquid-plume K-medoids calibration. Original folder and all files remain unchanged; extracted PDF text/renders and the durable audit are in private `analysis_outputs\older_v25_examples_audit_2026-11-02`, **not in this public repository**.

## Material and version provenance

The folder contains **1,584 objects (~3.011 GB)**: 1,075 TIFF, 418 PNG, 72 JPEG, eight 7z, five PDFs, five TXT and one CSV. Six experiment folders, including three literally marked **`[NOT DONE]`**. Although the folder is named for notebook v25, the **37-page PDFs' own page headers say `Dendrite & Plume Analysis v24.nb`**. Thus the PDFs document *earlier v24 configurations*, while [the versioned v25 notebook](../Mathematica_code/Dendrite%20%26%20Plume%20Analysis%20v25.nb) remains a separate original method source. No old notebook code or external scripts were run; PDFs were text-extracted with local `pdftotext` and selected pages visually rendered and checked.

### Case-specific MIL overrides (not the displayed generic/default values)

| Historical saved case | `thresholdFactor` | `dynamicThresholdBias` | `dynamicThresholdPower` | `solidSegmentSizeThreshold` | `liquidArtefactScale` | Source |
|---|---:|---:|---:|---:|---:|---|
| 2020-02-06, frame 502 | 17.5 | 22.5 | 1 | 25 | 50 | v24 PDF, pp. 10–11 |
| `[NOT DONE]` 2020-02-03, frame 311 | 2.45 | 3 | 15 | 25 | 200 | v24 PDF, pp. 10–11 |
| `[NOT DONE]` 2020-02-10, frame 487 | 18 | 22.5 | 1 | 25 | 50 | v24 PDF, pp. 10–11 |
| `[NOT DONE]` 2011-09-09 Experiment 2 | 20.5 | 15 | **−25** | 25 | 150 | `TEMP Settings Save.txt` |

All three 2020 PDF page 10s first list *generic/displayed* defaults `thresholdFactor=0.85`, `dynamicThresholdBias=3`, `dynamicThresholdPower=15`, `solidSegmentSizeThreshold=25`, followed by **different** shaded actual input assignments. Retain this distinction; don't promote defaults to case-specific values or silently change the negative power −25 recorded for the unfinished 2011 experiment.

For 2011 Exp2, the temporary file additionally lists `channelClosingScale=30`, `channelSizeThreshold=500`, `channelFillScale=15000`, `artefactBoundaryFrame=Length@cleanFrames` and `frontSmoothingFactor=3`. No proof that this unfinished recipe yields valid solid masks was found.

### Prior filtering and plume clustering

The 2020 v24 PDFs show the sequence: filtered/cleaned image → **time-dependent MIL segmentation** → solid/liquid and cavity/channel masks → liquid-mask inflation/front buffer → filtered liquid-only image → plume K-medoids clustering → ordering and morphological assembly. This is exactly the **segmentation-first approach** preferred by the owner.

The page references preserve distinct stages:

| Stage | Documented settings | Source |
|---|---|---|
| Frame denoising | `globalNonlocalMeansRadius=3`; case-specific preprocessing and time-dependent MIL correction | v24 pp. 7–10 |
| Bulk-liquid mask / front buffer | `maskInflation=15` | v24 p. 34 |
| Additional liquid filtering | `liquidGaussianKernelScale=3`, `liquidNeighborhoodRadius=2`, `liquidMedianRadius=1`, `extraNonlocalPatchSize=1`, `extraNonlocalScanRadius=15`, applies `NonlocalMeansFilter` | v24 p. 35 |
| K-medoids levels | `clusterCount=9`, `clusteringMethod="KMedoids"`, `colorSetID=97` | v24 pp. 35–36 |
| Level-set plume assembly | **active overrides** `plumeOpeningScale=1`, `maxLevelSetOrder=1` in each 2020 PDF; *displayed defaults* 5 and 2 | v24 p. 36 |

The original v25 source uses time-dependent `getDynamicThresholdFactor` and a pixel threshold depending on the **filtered MIL time series**, not merely a static threshold per frame. The existing v25 `MILbasedSegmentation` uses `allFilteredFrames[[frameID]]`, `selectedFrameIDs[[frameID]]`, `dynamicThreshold[[...]]`, `Binarize`, `ColorNegate` and `DeleteSmallComponents`. Consequently a single-frame contrast threshold cannot be called a reproduction of MIL.

**Critical status limitation:** In the saved 2020 result directories, stages `24_plume_level_sets.png`, `25_plume_decomposition.jpg` and `26_plumes_assembled_1.jpg` are **not present**, despite the clustering cells appearing in the 37-page PDFs. Thus the snapshots demonstrate *documented settings*, **not exported/validated plume segmentation output**. The saved `11_selected_frame_solid_boundary.jpg` images *do* document visual solid segmentation output. The 10-page `Experiment_...pdf` snapshots show front/kinematic and **relative-unit** concentration-like plots, not a calibrated absolute In wt.% field.

## Saved image corpus and exact pairing hazards

- **2020-02-06**: `Filtered Frames.7z` contains **502** `Filtered Frames/Frame_N.txt` strings, and `Solid Mask Overlays.7z` contains **502** `Sample_N.jpg` *rendered* solid overlays. A selected original `Frame_502.txt` was extracted safely; it is a Wolfram `1:eJw...` compressed image, decodable with licensed local Mathematica `Uncompress` as `Image`, `Real32`, **762×527 pixels**, numerical data range **0.6682–1.0523**. The matching-numbered `Sample_502.jpg` was visually inspected. **JPEG overlays are not binary ground truth**.
- `[NOT DONE]` 2020-02-03: 311 filtered text images and 311 solid overlays. `[NOT DONE]` 2020-02-10: 487 and 487. `[NOT DONE]` 2011-09-09 Exp2: 342 and 342. These matched *counts* do not independently prove raw-acquisition frame identity or scientifically accepted masks.
- **2014-03-07**: **500** `Frame_N.tiff` in `1 Cropped Images` and **418** `Frame_N.png` in `Solid Domain Masks`, with **418** recorded source-frame IDs, 600–2685 at interval 5. Direct independent Mathematica imports for selected indices 1,100,300,418 give **cropped TIFF dimensions 567×276**, while binary solid-mask PNGs are **763×384** (same mismatch for all checked). *No verified crop/transform or source-to-mask frame-index map exists*: **do not compute direct pixelwise Dice, blindly resize or infer exact correspondence from numeric basenames**. The masks show a growing white-solid region visually, but should be treated as historical outputs rather than independent human labels.
- **2011-09-09 Exp1**: 575 `Frame_N.tiff` examples, no matching exported binary solid-mask series within this supplied folder.

The examples can seed a physical segmentation parameter sweep once image/mask coordinates and temporal indexing are registered. They do **not** independently provide calibration anchors, camera timing, physical wall/crop provenance or paired concentration/OFV for G0.

## Controlled next validation steps

1. **2020-02-06 as historical MIL configuration baseline**, with the original 502 filtered Mathematica images, visual solid overlays, corresponding 2020 PDF/figure and documented actual v24 MIL assignments. Reconstruct temporal MIL *from correct source/reference data and frame selection* before claiming method fidelity. The saved filtering output is a useful intermediate, not evidence that raw detector frames or camera clocks are available.
2. Preserve the **alternative 2020-02-03/10 and 2011-09-09 Exp2** as independent sensitivity/out-of-sample, with `[NOT DONE]` status retained. Never fit parameters and validate on the same archived overlay examples without a held-out subset and manual adjudication.
3. Recover the exact **2014-03-07 image–mask coordinate and time map** before numerical mask concordance; the mask and cropped TIFF are different shapes.
4. After a validated solid-region mask, evaluate plume `K={9,12,16,24,32}` *within the physical liquid domain*, with pre-filter variants (median, bilateral, nonlocal, edge-preserving). Keep unmasked higher-K results as a negative control. Require independent manual plume/bulk annotation and stability rather than mere cluster occupancy.
5. Preserve original uint16/float source radiometry; normalization/histogram stretching for clustering is allowed only on a separate segmentation copy. The separate three-point `P↔C_In` measurement-anchor calibration and G0 source geometry/time admission remain **open**.

**Full source-audit working files:** `X:\AI-Lab-Test\Solidification_OFV\analysis_outputs\older_v25_examples_audit_2026-11-02\HISTORICAL_MIL_PLUME_PARAMETER_AUDIT.md`, raw PDF text, rendered visual pages, `parameter_index.json` with page/line matches, and selected imported-frame visualizations. No raw data or screenshots committed publicly.
