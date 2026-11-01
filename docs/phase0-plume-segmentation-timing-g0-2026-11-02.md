# Phase 0 — independent time registration and notebook-informed segmentation study

**Status:** New, separately reviewable Phase-0 timing contract. Experimental G0 is **not fully closed**. This document records a scientific, read-only assessment of the upstream notebook's segmentation approach and a local prototype. It does not modify the original notebook or use segmentation labels as composition measurements.

## Source identity and safe inspection

- Repository source: [`Mathematica_code/Dendrite & Plume Analysis v25.nb`](../Mathematica_code/Dendrite%20%26%20Plume%20Analysis%20v25.nb), 814,430 bytes, Git blob SHA `b13ef6adda22405d89680e3ebe5da50e6f40d297`.
- The exact file was downloaded as an **analysis working copy** to `X:\AI-Lab-Test\Solidification_OFV\analysis_outputs\phase0_scout_2026-11-01`, verified with `git hash-object`, and **parsed as a Notebook expression using the licensed local Mathematica 12.1 WolframScript kernel**. The original notebook, its historical `InitializationCell` expressions, and external package imports were **not evaluated or modified**.
- The notebook defines `MILbasedSegmentation` (time-dependent mean inverse luminance threshold, image binarization and small-component cleanup) for solid-region masks, liquid cavities and channel masks, dendrite-region skeleton/morphological analysis, and a **9-level liquid-region clustering method**: `getClusters[image_] := ClusteringComponents[image,clusterCount,Method->clusteringMethod]`, with notebook settings `clusterCount=9`, `clusteringMethod="KMedoids"`. It separately uses liquid-mask inflation (`maskInflation=15`), filtering including median/bilateral/nonlocal/Gaussian methods, cluster colorization and ordered level sets; `plumeOpeningScale=5` and `maxLevelSetOrder=3` are specified in the recombination section.
- The notebook's `getFilteredConcentrationField` name is not itself evidence of a concentration-to-luminance calibration law. Its region clustering acts on preprocessed image intensities. Accordingly region classes must be independently labelled/verified before any liquid composition calibration can be accepted.

## Actual isolated exploratory notebook-method pilot

The authorized X: workspace contains original 2014-01-15 760×560 uint16 experimental/reference/dark TIFFs and the paired radiometric scripts/results (see [prior raw-data report](phase0-historical-raw-radiometry-2026-11-01.md)). A **single time-selected experimental image** was tested using the *same fixed central 200×200 pixel patch* (image y indices 181–380, x indices 281–480, Mathematica 1-based).

Two radiometric alternatives were computed from the unaltered raw counts (using five frame-mean reference and dark images): (A) reference-only `g=-ln(I/R)` and (B) dark-corrected `g=-ln[(I-D)/(R-D)]`, defined only where `I>D` and `R>D`. No negative g was silently clipped in the quantitative arrays. For **segmentation and visualization only**, separately normalized/clipped views (shared `g` display window -0.05 to +0.20) received one-pixel Gaussian filtering and `ClusteringComponents[...,9,Method->"KMedoids"]`. Both generated nine numerical classes and separate colorized PNGs; neither received a physical solid/plume/bulk-liquid label.

| Numerical pilot property | Reference-only | Dark-corrected |
|---|---:|---:|
| Local raw input patch | 200×200 | 200×200 |
| Positive-ratio pixels in patch | 40,000 | 38,628 (96.57%) |
| Median unmodified optical density g (on valid patch pixels) | +0.007806 | +0.058518 |
| KMedoids image levels generated | 9 | 9 |

The full-frame dark-corrected valid fraction for the same middle experimental sample was only **58.29%** (see previous report). The contrast with **96.57% valid within the arbitrary central patch** is evidence that spatial selection greatly affects admission, **not** evidence that the chosen crop is entirely within the physical cell or free of artefacts. The class counts and all PNGs are retained *locally* for diagnostic inspection. A Gaussian-only, fixed-patch clustering pilot **is not a full execution of the v25 pipeline**: it omits the full-sequence MIL-based solid mask, validated liquid-channel/bulk masks, and the notebook's more extensive filtering. It does not identify plume chemistry, validate region purity or measure composition.

## Recovered three-point physical calibration (method, not case-specific coefficients)

A project methodological note, **Natalia Shevchenko, HZDR, `Concentration_mapping_intermediate.docx`**, specifies the physical anchor method. Its signal is `P=-ln(I/I0)` using *dark-current-corrected* experimental and reference intensities. The pre-solidification melt `C0=25 wt.% In` defines `P=0`. After solidification, an indium-rich dendrite reference `C_In≈98.6 wt.%` is assigned under a **full-cell-thickness dendrite** assumption; a Ga-rich liquid channel is independently anchored at about `5–10 wt.% In` using a pure-gallium comparison. The three `(P,C_In)` points underpin a *semi-quantitative* empirical mapping. This is separate from Kristofers' later calibrated `C_In = 270.1341*g + 29.2945` for a different acquisition, and from any 2014 source-specific fit. No actual `P` values for the 2014 historical reference regions, uncertainty/fit covariance or independent validation labels were established in the present selected samples. Do not transfer coefficients or infer 98.6%-pure solid from projected luminance without verifying physical thickness.

The associated published methodology is [Birjukovs, Shevchenko and Eckert, *Experiments in Fluids* (2023), DOI:10.1007/s00348-023-03671-2](https://doi.org/10.1007/s00348-023-03671-2). Section 2 reports for the imaged HZDR study a **35×25×0.15 mm Hele-Shaw cell**, **1 image/s with 1 s exposure**, typical **~760×576 16-bit TIFFs**, and a **13.7–37.6 μm** pixel-size range varying by dataset/crop. This independently supports the general *one-second nominal cadence* found in archived filenames, but it is **not** an exposure log or a per-archive geometrical calibration: original device/crop provenance still needs verification. Published Algorithm 9 applies median/bilateral/nonlocal filters and a solid-front buffer for liquid-zone luminance sampling, with optional Beer–Lambert composition conversion; Algorithm 10 separately applies a liquid-zone mask/front buffer, additional filtering and K-medoids luminance level sets for plume morphology. In the 2023 paper, measured liquid luminance was also plotted in **relative units**; this is not equivalent to validated absolute In wt.% concentration maps.

**Proposed semi-automatic extension:** first validate solid-zone and Ga-rich-channel candidate masks and verify whether the high-In dendrite truly spans the X-ray thickness, then compute each anchored `P` on the untouched radiometric branch, perform a weighted/uncertainty-aware calibration with a held-out region and compare dark/no-dark sensitivity. Never let an intensity K-medoids group automatically determine its own chemical label.

## Implications for a calibrated three-region model

Proposed separation, conditional on reference labels/ground truth:

1. Derive a *physical-domain mask* and known chamber boundaries from full original geometry. Distinguish permanently invalid/saturated detector pixels; never force their values into a cluster.
2. Compare `I/R` and `(I-D)/(R-D)` against independently grounded illumination/detector stability, using the **same reference and time-selected image domain**. Preserve both results, validity masks and sensitivity bands.
3. Pre-filter **only segmentation copies** for solid/plume/bulk-liquid identification. Protect raw counts and untouched quantitative optical density; do not histogram-match or stretch them to form composition.
4. Recover solid geometry using MIL-derived threshold, temporal persistence and morphological cleaning. In the validated liquid portion only, test nine-level KMedoids and reduced/alternative level counts. Color/order classes by *physical optical density* after clustering, not by display color.
5. Validate candidate plume versus bulk liquid using manual labels, morphology, time persistence and flow evidence. Reject regions where the segmentation is ambiguous. No "plume" assignment is certified by an unsupervised intensity cluster alone.
6. Apply the manually established concentration↔luminance relation **only within a physically appropriate, calibrated liquid-phase domain**, with units, reference composition, fit coefficients, interval of validity, independent holdouts and uncertainty. Do not apply it to solid areas solely because their brightness resembles a liquid class.

This segmentation workflow may help make manual concentration calibration semi-automated, but **does not supply the calibration anchors**.

## Independently implemented timestamp and concentration *association* contract

The original [`Python_code/phase0_time_registration.py`](../Python_code/phase0_time_registration.py) is standard-library only. It consumes explicit `raw_frames`, `image_bins`, `concentration_frames` and `flow_pairs`, each with source IDs and numeric acquisition times supplied by a manifest. It refuses missing, duplicate, non-monotonic, overlapping and gap-crossing source frames, mismatched composition times, and non-adjacent pair IDs; it returns each flow-pair *midpoint time* and two **bracketing concentration-image IDs with interpolation weights**, without opening or altering TIFFs.

The `clock_source` is explicitly one of `camera_metadata`, `verified_acquisition_log` or `filename_candidate`. The last is **diagnostic-only**, never authoritative. The code does not invent `dt0` from a notebook, title, AVI video, or archive naming, and does not presume the actual source has B=5 frames per bin. Scientific concentration interpolation itself remains a **separate** method to be validated after radiometry and physical registration.

### Example (synthetic ground truth only)

For raw frame-center times `0,0.2,0.4,...,2.8` s, three five-frame bins have times `0.4,1.4,2.4` s. Flow-pair centers are `0.9` and `1.9` s, and the temporal interpolation weights between neighboring concentration-bin images are `(0.5,0.5)`. With actual one-second source intervals, the same nominal bin sizes instead produce image-bin centers `2,7,12` s and flow-pair centers `4.5,9.5` s. **Neither timing may be assigned to real archival data without independent clock provenance and an actual bin manifest**.

Run the offline unit suite with `python -m unittest discover -s tests -p "test_*.py" -v`. No scientific frame data are needed. The module does not certify physical spatial registration or full concentration interpolation.

## Second archive spot check — averaged calibration TIFFs are NOT source-equivalent

The `2014-04-15-Exp2.7z` archive includes TIFFs named `ga-25in-ref2.txt, Averaged.tif` and `ga-25in-dark2.txt, Averaged.tif`. The exact owner source archive was read through native 7-Zip; four first/last/source-average TIFFs were selectively extracted, and then **one original individual reference TIFF** and **one individual dark-current TIFF** were additionally extracted with exact `-i!full/internal/path` selectors. All six are 762×499 uint16 samples. The archived averaged reference and dark fields have mean stored counts ~28,718 and ~28,329, while the selected original reference and dark exposures have mean counts ~57,832 and ~52,182 respectively. Pointwise average/single ratios are not constant (median ~0.377 for reference and ~0.407 for dark), so the archived averages **cannot be assumed interchangeable with the source exposures or recovered by blindly doubling them**. The actual historical averaging/export method is not yet established. This alone prohibits unreviewed quantitative use of those averaged files.

For two experimental frames, the admitted dark-corrected fractions and median `g` differ markedly depending on which TIFF reference/dark pair is selected:

| Experiment frame | Using archived 'Averaged' ref/dark: fraction / median g | Using one original ref/dark: fraction / median g |
|---|---|---|
| First | 0.6233 / -1.5674 | 0.7976 / +0.00149 |
| Last | 0.6171 / -1.4832 | 0.6048 / +0.45867 |

The underlying **reference-only** signal `g=-ln(I/R)` on the single original reference has median ~+0.00054 (first) and +0.06022 (last). These are all *diagnostic, uncalibrated* optical densities; neither a single reference/dark exposure nor a file labelled 'Averaged' is an automatically validated radiometric correction. The original reference/dark sets and detector dark stability must be checked in aggregate before interpreting these fields. Analysis JSON and scripts remain on the authorized X: workspace; no experimental pixels were published in GitHub.

## G0 gate decision

| G0 item | Current state |
|---|---|
| Original 2WCF numerical core and saved-vector format | Verified on 80-frame processed test; 79/79 pairs reproducible |
| 2WCF output orientation, image-domain/Cartesian reflection | Verified; merged PR #3 |
| Six raw archives accessible; source TIFFs decoded | Verified, source CRC complete for one archive |
| 2011 historical source folder identified | Source path matched, exact raw-vs-clean variant still ambiguous |
| Dark-corrected vs no-dark optical-density comparison | Completed on representative samples, *quantitative admission refused* |
| Solid/plume/bulk mask method | Notebook inspected, 9-level exploratory segmentation runs, **not physically validated** |
| Acquisition timestamps and pair-to-composition temporal association | Contract prepared; real full manifest + camera-clock verification outstanding |
| Concentration-to-luminance fit for this acquisition | Manual method known to user, **actual calibrated anchors/parameters not yet verified** |
| Physical crop/walls and same-experiment quantitative concentration/OFV | Not established |
| Experimental continuity/energy closure | Not attempted; beyond G0 admission |

**Decision: G0 remains OPEN, but the tools/data now make closure feasible after providing/locating the actual calibration anchors, a verified source-to-processed mapping and physical cell geometry.** Do not conflate a runnable code contract or segmented image with accepted experimental physical inference.
