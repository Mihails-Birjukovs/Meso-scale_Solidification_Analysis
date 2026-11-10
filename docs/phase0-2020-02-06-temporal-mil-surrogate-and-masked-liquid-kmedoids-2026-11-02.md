# Phase 0 — 2020-02-06 saved-image temporal MIL surrogate and liquid-only K-medoids admission

**Date:** 2026-11-02 (Europe/Riga). **Status:** `DIAGNOSTIC_ONLY_NOT_SOURCE_EXACT`; **G0 remains OPEN**. This report records local Mathematica 12.1 experiments on user-supplied **private historical processed images**. It neither runs the whole archived v24 notebook nor modifies the authoritative [v25 notebook](../Mathematica_code/Dendrite%20%26%20Plume%20Analysis%20v25.nb). No measured pixels or historical model output images are committed to this public repository.

## Basis, provenance and critical source-fidelity distinction

The supplied `older_output_examples_Dendrite_Plume_Analysis_v25_NB` folder includes a 37-page PDF snapshot whose **actual page header says `Dendrite & Plume Analysis v24.nb`**. Its **2020-02-06** case shows active MIL settings `thresholdFactor=17.5`, `dynamicThresholdBias=22.5`, `dynamicThresholdPower=1`, and `solidSegmentSizeThreshold=25`; it also records temporal Total Variation filtering parameters `weight=0.01`, `MaxIterations=500`, `Method="Gaussian"` (pp. 7–10). The notebook sets `lowerLimit=1400`, `imageStepSize=5` and chooses source-frame indices from that start. A separately archived `Filtered Frame IDs.txt` was decoded in local Wolfram Mathematica using `Uncompress`: it is **exactly the 502-element sequence** `1400, 1405, …, 3905`. It is therefore legitimate to associate saved filtered image `Frame_j` with source **index** `1400+5(j-1)`. This is **not** an independently verified physical acquisition time.

The `Filtered Frames.7z` contains 502 Mathematica-compressed `Frame_j.txt` image objects (analyzed as original files, independently extracted as temporary working copies into the authorized X: analysis area); each decoded image is **Real32, 762×527**. The corresponding `Solid Mask Overlays.7z` contains 502 historical visual `Sample_j.jpg` overlays. Historical sample overlays are **1500×1037 JPEGs**, *not* binary segmentation masks or independent manual truth.

**Non-equivalence of temporal source:** The original notebook's `getMILseries` computes Mean Inverse Luminance from the **full original `images` time series**, applying the original reference flat-field correction, Gaussian filtering, `ImageAdjust` and `ColorNegate`. The supplied files retain only **502 later filtered/selected images**, not the original ~3,905 preselected frames nor the original numerical MIL vector. Therefore the experiment below computes a **surrogate** temporal MIL from already filtered images. It is not an exact original-threshold or full-v24/v25 pipeline replay. A visually plausible result cannot erase that missing upstream source.

## Full processed-image surrogate MIL and solid mask study

The local `surrogate_2020_02_06_mil_replay.wls` computes, for every saved filtered image `F_j`,

`m_j = Mean[Flatten[ImageData[ColorNegate[ImageAdjust[F_j]], "Real32"]]]`.

It then applies a **temporal** `TotalVariationFilter` with the historical TV settings to the 502-point surrogate MIL trace, constructs the v24-style dynamic factor using `dynamicThresholdBias=22.5` and the time-series `Max`/`Min` normalizations, then `tau_j = 1 - 17.5*10^-2*m_filtered,j*factor_j^1`. The new per-frame mask candidate is

`DeleteSmallComponents[ColorNegate[Binarize[F_j,tau_j]],25]`.

Both scripts and outputs are local X: files. There is **no physical solid fraction or composition measurement** implied by the resulting binary mask.

| Surrogate MIL study output | Actual result |
|---|---:|
| Decoded and temporally indexed filtered images | **502/502** |
| Processed image dimensions and type | **762×527, Real32** |
| Surrogate MIL scalar range (pre-TV) | **0.17952–0.38810** |
| Surrogate thresholds `tau_j` | **0.93307–0.96722** |
| Individually exported candidate solid masks | **502** |
| Candidate solid fraction, first/last mask | **1.967% / 64.417%** |
| Candidate solid fraction, overall maximum | **64.732%** |
| Consecutive *saved-frame* binary IoU, median | **0.96413** |
| Consecutive saved-frame IoU, minimum/maximum | **0.87277 / 0.97599** |
| Area-fraction decreases from one saved frame to next | **160 of 501 intervals** |

The 502 binary PNG masks, source-index / threshold / mask-area / consecutive IoU CSV, and validated JSON summaries are preserved privately. IoU is a **self-consistency** diagnostic of this derived mask series, *not Dice/IoU against validated reference masks*. Growth is substantial overall but **not strictly monotonic**, motivating time-regularization and physical-front verification.

### Visual comparison to historical overlays

Read-only original archive exports `Sample_1.jpg`, `Sample_50.jpg`, `Sample_250.jpg` and `Sample_502.jpg` were selected, and qualitative side-by-side views were created against the corresponding new surrogate overlay images. The principal dendrite branches/liquid channels visibly correspond in the late case, but the new overlays are smoother and differ in fine boundary placement. Historic JPEGs are **1500×1037**, candidate fields **762×527**, so the historical JPEGs were resized for *display only*. No blind image registration, pixelwise Dice, or accuracy score was claimed, and the legacy JPEG overlay should not be silently converted into ground-truth binary solid labels.

## True masked candidate-liquid K-medoids sensitivity

After the surrogate solid mask, the study selected candidate **liquid-only** pixels (`solidMask==0`) inside an identically defined **300×300** Mathematica 1-based crop, rows 101–400 and columns 231–530. Saved frame 250 (source index 2645) had **71,184** liquid pixels in this crop; saved frame 502 (source index 3905) had **31,605**. The source processed intensity arrays were preserved without physical concentration conversion or quantitative OD clipping.

Crucially, the excluded solid pixels **do not enter K-medoids training** and remain class **0** in result images. A deterministic sample of up to **2,000 liquid values** was clustered using `ClusteringComponents[Image[{sample},"Real32"],K,Method->"KMedoids"]`; one-dimensional centers for each cluster were selected as data-valued sample medians. All candidate liquid pixels were assigned the closest 1D center; results were colorized **for visualization only**. This sampled, liquid-only **one-dimensional intensity model is not exact numerical equivalence** to v24/v25 whole-image `ClusteringComponents`; it is an isolated scientific experiment designed to avoid allocating a medoid to masked solid/background.

Forty runs were completed: saved frames 250 and 502 with filters *none* and Gaussian 1 px at `K=9,12,16,24,32`; plus frame 502 with Gaussian 3 px, median 1 px, nonlocal means (patch 1, scan radius 15) and bilateral filter (value spread 3, kernel 21), again at all five K. The alternative filters are **independent sensitivity branches**, not automatically the original notebook's sequential liquid-filter pipeline.

| Frame 502 prefilter | RMSE at K=9 | RMSE at K=32 |
|---|---:|---:|
| None | 0.003194 | 0.000925 |
| Gaussian 1 px | 0.003277 | 0.000962 |
| Gaussian 3 px | 0.003783 | 0.001229 |
| Median 1 px | 0.003266 | 0.001061 |
| Nonlocal means 1/15 | 0.004704 | 0.001562 |
| Bilateral 3/21 | 0.004549 | 0.001468 |

These are **within-liquid one-dimensional quantization RMSEs in the corresponding filtered image-intensity units**. Filtering changes the target intensity field, so these RMSEs **must not be interpreted as ranking filters for plume accuracy**. Increasing K generally reduces quantization error by construction; class occupancy and lower RMSE do not identify physical plumes or make any mass-fraction calibration valid. All 40 class-size arrays sum to the admitted liquid pixel count, and each run reports the medoid values, seed and file identity.

At frame 250, the none/Gaussian-1-pixel branches gave RMSE **0.002001/0.002093 at K=9**, and **0.000699/0.000664 at K=32**. At frame 502 the branch values are in the table above. Data and individual class-preview PNGs are local only.

## Scientific admission decision and next steps

| Question | Decision |
|---|---|
| Can all **saved filtered frame IDs** be associated with original notebook indices? | **YES**, exact 502-element list matches the documented 1400/5 mapping |
| Is each archived image decoded and a reproducible temporal surrogate computed? | **YES**, native Mathematica processed all 502 |
| Are new **502 surrogate binary masks** reproducibly generated and internally time-consistent? | **YES**, masks/CSV/manifest and sampled IoU audit stored |
| Does the surrogate reproduce the **original full-sequence MIL**? | **NO**, original upstream `images`, flatfield reference and original MIL vector unavailable in the checked example folder |
| Are the saved historical overlay JPEGs independently accepted binary ground truth? | **NO**, dimensions differ and annotations are renders |
| Does masked K-medoids produce candidate liquid intensity levels at K=9–32? | **YES**, 40 exploratory runs, not chemical plume identification |
| Has experiment-specific chemical `P↔C_In` calibration been validated? | **NO** |
| Are same-source quantitative OFV/concentration geometry, clock and radiometry admitted? | **NO; G0 REMAINS OPEN** |

**Next valid acceptance work:** acquire the *original* 2020-02-06 upstream image sequence, flatfield reference and saved original MIL or reproduce it from confirmed source inputs; recover original binary solid masks or independently label a held-out sample (not just JPEG outlines); quantify source-to-overlay display transforms; compare surrogate vs source-exact methods with mask IoU/Hausdorff/front-location errors on identical domains. Then run full sequence-dependent v25 solid segmentation and use accepted liquid masks to evaluate plume-level stability over time and across prefilters, with manual plume/bulk regions. Only after this, connect physically grounded radiometric anchors, composition and independently registered OFV fields. No full flow conservation or energy balance is claimed at this gate.

## Private reproducibility record

The authorized X: working root is `X:\AI-Lab-Test\Solidification_OFV\analysis_outputs\older_v25_examples_audit_2026-11-02`. Important scripts: `inspect_2020_ids.wls`, `surrogate_2020_02_06_mil_replay.wls`, `full_502_surrogate_mil_masks.wls`, `masked_liquid_kmedoids_2020_02_06_v2.wls`, `masked_liquid_kmedoids_2020_02_06_v3_filters.wls`, `compare_saved_jpg_versus_surrogate_overlays.wls`, `verify_surrogate_and_masked_kmedoids_qa.py`. Generated directories contain PNG masks, 40 class previews, CSV source indices and metrics, JSON manifests and visual comparisons. The experimental files, source archive, raw compressed frame copies and images are **not distributed** in this repository. For reusable code delivery, these research scripts should be generalized to explicit data-path/config inputs and independently reviewed; absolute X: paths are *local execution provenance*, not portable package paths.
