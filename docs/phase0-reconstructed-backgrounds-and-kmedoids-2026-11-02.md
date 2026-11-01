# Phase 0 — notebook-acquisition metadata, full reference/dark means and K-medoids level sweep

**Status:** Read-only scientific QA; **G0 still OPEN for physical composition admission**. Findings as of 2026-11-02. This report supplements [original raw TIFF audit](phase0-historical-raw-radiometry-2026-11-01.md) and [previous notebook/timing admission](phase0-plume-segmentation-timing-g0-2026-11-02.md). PR #6 was approved and merged at `cc5120223777ce675ee2ee1c62a6c9b2f779e8e6`. Experiment images and generated TIFFs remain on authorized private X: storage, not this public GitHub repo.

## Direct notebook source: specific pixel size and exposure metadata

The unchanged [`Mathematica_code/Dendrite & Plume Analysis v25.nb`](../Mathematica_code/Dendrite%20%26%20Plume%20Analysis%20v25.nb), Git blob `b13ef6adda22405d89680e3ebe5da50e6f40d297` (814,430 bytes), documents in the **Import Images** section:

| Dataset as literally named in notebook | Pixel pitch, μm/pixel |
|---|---:|
| 2014-04-04 | 37.6 |
| 2014-03-07 | 37.6 |
| 2011-09-19-Exp2 | 23.7 |
| 2014-04-15-Exp2 | 17.3 |
| 2011-09-09-Exp1 | 17.5 |
| 2011-09-09-Exp2 | 17.5 |
| 2020-02-03 | 11 |
| 2020-02-06 | 17.5 |
| 2020-02-10 | 17.5 |

The notebook says **'Exposure time in all cases: 1 s'** and the active *2011-09-09-Experiment-1* import example assigns `pixelSizeMuMeters = 17.5` and `frameDurationSeconds = 1`. These are original recorded **notebook source metadata**. They are stronger than generic reported ranges, but do **not** prove any historical crop/resize/bin-to-OFV transform, camera-clock uncertainty, or every 2014-01-15 field (not specifically in the list). Do not transfer 17.3 μm/pixel to unrelated experiments or the March-2026 processed OFV source.

## Reconstruct original beam/reference and dark means from complete raw stacks

The user approved reconstructing **per-pixel arithmetic means directly from the raw beam/reference and dark TIFF sequences** while retaining an independent reference-only optical-density branch.

The original six source `.7z` archives remain unchanged. The earlier source-archive enumerations used exact full internal path 7-Zip includes and refused unexpected selection counts before expanding these **selected source TIFF copies** into `X:\AI-Lab-Test\Solidification_OFV\analysis_outputs\phase0_scout_2026-11-01`.

| Original archive | Original reference exposures | Original dark exposures | Per-pixel mean R (counts) | Per-pixel mean D (counts) | Fraction of pixels where reconstructed R is greater than D |
|---|---:|---:|---:|---:|---:|
| 2014-01-15 | 113 | 105 | 58,230.418 | 55,592.473 | 72.30% |
| 2014-04-15 Exp2 | 108 | 120 | 57,847.084 | 54,317.608 | 77.22% |

Mean *frame-wide* raw reference counts were tightly grouped: **58,192.13–58,270.35** for 2014-01-15 and **57,798.80–57,881.69** for 2014-04-15 Exp2. Dark-frame mean counts changed more: **54,041.20–56,334.98** and **51,751.05–55,532.51**, respectively. Both detector-background series contain pixels at/near 65,535 (16-bit saturation), and the full-cell mask, dark stability, raw image acquisition and beam current state have not been certified. A *mean* is a reproducible estimator, **not proof of a valid detector correction**.

Implementation: original local `reconstruct_reference_dark_stacks.py` accumulated all input 16-bit raw pixel counts into float64 per-pixel means, writing unscaled float32 single-channel TIFF reference, dark and reference-minus-dark. All are on X:, with `stack_reconstruction.json` including individual source TIFF SHA-256 and per-frame detector means. Independent Mathematica 12.1 `Import` checked TIFF dimensions and mean intensity, e.g. reconstructed 2014-01-15 R mean 58,230.418 and D mean 55,592.473. The generic public, dependency-free reconstruction tool is [`Python_code/phase0_reference_dark_reconstruction.py`](../Python_code/phase0_reference_dark_reconstruction.py), which similarly preserves raw-count means, refuses unknown TIFF encoding and source/target overwrites, records source hashes, and supports comparison to historic averages. Its synthetic tests are in `tests/test_phase0_reference_dark_reconstruction.py`. Re-running it against original X: data is a separate provenance check; do not equate matching algorithms with cross-environment byte identity before checking hashes.

### Persisted original 'Averaged' files are not recovered by reconstruction

For 2014-04-15 Exp2, the archive additionally contains `ga-25in-ref2.txt, Averaged.tif` and `ga-25in-dark2.txt, Averaged.tif`. When interpreted as ordinary unsigned 16-bit grayscale TIFFs:

| Object | Archived TIFF mean | True arithmetic raw-stack mean | Pixelwise correlation with stack mean | Pixelwise RMSE (raw counts) |
|---|---:|---:|---:|---:|
| Reference | 28,717.718 | 57,847.084 | +0.00442 | 34,465.59 |
| Dark | 28,329.149 | 54,317.608 | −0.00062 | 31,606.55 |

Neither swapping bytes, interpreting pixels as signed values, nor inverting unsigned intensity restores the spatial relationship. The archived TIFFs are therefore **not established as arithmetic means of these particular raw exposure stacks**. They may represent an undocumented transformation, different source subset or broken export; do not assert a definite corruption mechanism. No blind factor-of-two correction is admissible. A complete source ImageJ processing/export audit would be required before trusting them.

### Re-evaluated radiometry using reconstructed original means

For 2014-04-15 Exp2, using arithmetic mean R,D from the full stacks, strict validity `I>D && R>D` and **no clamping**:

| Experimental frame | Full-field valid pixels for dark-corrected ratio | Central exploratory 200×200-pixel ROI valid pixels | Median full-field g, reference-only | Median full-field g, dark-corrected |
|---|---:|---:|---:|---:|
| First | 75.92% | 99.97% | +0.0008 | +0.0033 |
| Last | 46.88% | 74.43% | +0.0601 | +0.5990 |

The analogous 2014-01-15 first/middle/last full-field dark-domain valid fractions are **71.11%/59.22%/41.10%**, whereas the same arbitrary central ROI is **99.99%/96.99%/88.19%**. Spatial selection determines strong differences, **but the arbitrary ROI is not yet certified as the true chamber/valid liquid geometry**.

Reference-only `g=-ln(I/R)` is retained as a mandatory comparator, alongside dark-corrected `g=-ln[(I-D)/(R-D)]`; both keep negative g values as mathematically valid where the ratio is positive. Pixels with nonpositive corrected intensities are explicitly invalid, never set to zero in *quantitative* arrays. No pixel has been converted to In wt.% in this pass.

## User-directed plume-level clustering experiments

The original v25 notebook **separates the solid zone first**, then performs luminance K-medoids classification in the admissible liquid zone with nine original levels. This separation matters: otherwise the level budget is spent on solid, artefact and liquid intensities, not necessarily on the plumes. The notebook's `MILbasedSegmentation`, channel/cavity masks and Algorithm-10 front buffer are an appropriate baseline once run and checked on the selected full sequence.

As a first **deliberately unmasked** stress test, local Mathematica 12.1 evaluated `ClusteringComponents[..., K, Method->"KMedoids"]` with `K=9,16,24`, on (i) unfiltered intensity copies and (ii) 1-px Gaussian-smoothed copies, on the *same 200×200 central patch* of the 2014-01-15 middle original frame. Both the reference-only and reconstructed-dark-corrected OD fields were used. The dark-corrected field contains **38,797/40,000 (96.99%)** valid quantitative pixels. For the **segmentation branch only**, per-branch 1st/99th percentile intensity normalization/clipping and invalid-pixel fill were applied; the actual OD/calibration fields were untouched.

| Branch | Prefilter | K | Observed nonempty clusters | Smallest–largest cluster, pixels |
|---|---|---:|---:|---:|
| Reference-only | None | 9 | 9 | 997–9,631 |
| Reference-only | None | 16 | 16 | 675–4,876 |
| Reference-only | None | 24 | 24 | 608–2,652 |
| Reference-only | Gaussian 1 px | 9 | 9 | 1,005–9,475 |
| Reference-only | Gaussian 1 px | 16 | 16 | 630–5,062 |
| Reference-only | Gaussian 1 px | 24 | 24 | 518–3,003 |
| Dark-corrected | None | 9 | 9 | 670–12,760 |
| Dark-corrected | None | 16 | 16 | 455–5,176 |
| Dark-corrected | None | 24 | 24 | 365–2,847 |
| Dark-corrected | Gaussian 1 px | 9 | 9 | 719–11,132 |
| Dark-corrected | Gaussian 1 px | 16 | 16 | 604–4,732 |
| Dark-corrected | Gaussian 1 px | 24 | 24 | 288–3,065 |

The 12 colorized diagnostic PNGs, validity mask, executed `.wls` script and JSON class distributions are stored **privately** in `kmedoids_level_sweep_2014-01-15`. This confirms that extra medoids are computationally feasible and create finer intensity partitions in an unmasked case, **not** that 16/24 is more physically correct or identifies a verified plume. Unmasked dark-corrected segmentation can allocate classes to invalid-zero placeholder pixels: future source segmentation should isolate valid pixels or distinguish a mask label explicitly and must **not** use these placeholders to assign composition. A 200×200 crop at one time does not reproduce full notebook Algorithm 10 or establish robust temporal plume labels.

**Recommended controlled follow-up:** after reconstructing and validating full-sequence MIL solid masks, repeat a fixed `K={9,12,16,24,32}` (or similar) sweep with/without physical solid masks and alternative pre-filters (median, bilateral, nonlocal, edge-preserving; avoid smoothing away faint plume gradients). Compare stability over time, held-out labels and manual anchor areas; measure K-medoids sensitivity to camera/radiometry choice and take only liquid-region masks into composition estimation. Never automatically substitute cluster numbers for chemical mass fractions.

## Additional original-stack pairs recovered from the six-archive census

The complete six-archive filename census identified *two additional original reference + dark stack pairs*, so four independently reconstructed reference/dark pairs are now available on X:. A crucial provenance detail: the `2011-09-19.7z` archive contains both original images under `2011-09-19/2011-09-19` **and cropped-left-side derived duplicates** under `2011-09-19/2011-09-19-cropped-left-side`. Its first naive `ref1`/dark enumeration counted 202 of each, but **only 101 reference and 101 dark are original full-frame measurements**. Derived crops were not mixed into the raw averages. `2011-09-19` `ref2` and `2013-01-10` `ref2`/`ref3` are distinct reference recording groups, intentionally excluded from the `ref1+dark1` means until their experimental correspondence is justified.

| Original source acquisition and paired input group | Raw mean R frames | Raw mean D frames | Decoded source size | Reconstructed R / D, counts | Pixels with R>D |
|---|---:|---:|---|---|---:|
| **2011-09-19 ref1 + dark1** (uncropped originals only) | 101 | 101 | 755×444 | 54,106.876 / 53,218.198 | **65.35%** |
| **2013-01-10 ref1 + dark1** | 103 | 103 | 756×542 | 57,247.210 / 54,911.807 | **67.80%** |
| 2014-01-15 ref1 + dark1 | 113 | 105 | 760×560 | 58,230.418 / 55,592.473 | 72.30% |
| 2014-04-15 Exp2 ref2 + dark2 | 108 | 120 | 762×499 | 57,847.084 / 54,317.608 | 77.22% |

For the two newly reconstructed acquisitions, frame-wide reference mean ranges were **54,059.20–54,165.79** (2011) and **57,192.33–57,286.92** (2013); corresponding dark-frame mean ranges were **51,099.15–54,518.44** and **54,323.44–55,181.02**. All selected source TIFFs were extracted only as read-only-analysis working copies after exact full-path 7-Zip selection preflight; originals remain untouched. Executions of the **GitHub branch's own hash-verified generic reconstruction script** saved three float32 TIFFs plus per-source SHA-256 manifest and per-exposure stats, respectively:

- `reconstructed_pr7_2011-09-19_ref1_dark1`: R, D, R−D TIFFs and `manifest.json`;
- `reconstructed_pr7_2013-01-10_ref1_dark1`: R, D, R−D TIFFs and `manifest.json`;
- `reconstructed_pr7_2014-04-15-Exp2`: R, D, R−D TIFFs and `manifest.json`.

For `2014-04-15 Exp2` the new GitHub implementation's two reconstructed mean TIFFs are **byte-for-byte SHA-256 identical** to the original, independently developed local reconstruction prototype: reference `ab868a99d6db977b73775efbae1b146bb5f243fc567b1b3e1b0b07b558cc2d91`, dark `235cfb0812e58fc06bf6a4ecda71e5c169d0d704ad1347d6b3ff393fe30fb946`. Generic helper script downloaded from the PR #7 branch was verified with Git blob `0539407659e93dec9f4173a8bf23438dbdf751ef` before running. Thus this **specific** data pair has cross-script byte-level reproducibility as well as synthetic tests.

The other two archives, `2011-09-09` and `2014-04-04`, include original beam/reference TIFFs but no matching dark-exposure TIFF groups identified in the archive census. They remain candidates for **reference-only** processing; do not fabricate dark profiles. The notebooks' `2011-09-19-Exp2` 23.7 µm/pixel value must not be assigned to `2011-09-19 ref1` without confirming the experiment/crop correspondence. The new original-background data do not close G0 because no detector transfer-function stability, valid physical mask, or calibrated same-acquisition composition pair has been accepted.

## G0 decision

**G0 remains OPEN** for reliable experimental physical interpretation. We now have dataset-specific notebook exposure/pixel metadata, independent full-stack mean reference and dark TIFFs for two experiments, isolated K-medoids level-sensitivity tests, and previously validated OFV core/direction and a separate synthetic-tested temporal association tool. Still missing: source-specific camera clock and raw→processed→OFV frame/crop mapping, physical chamber/cell mask, validated solid/plume/liquid masks, original measurement-backed reference and dark transfer/averaging provenance, registered 25/98.6/5–10 wt.% calibration *P* anchor values and a matched same-run quantitative concentration/velocity pair. Full mass/energy validation belongs after G0.
