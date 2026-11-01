# Phase 0 — Raw TIFF radiometry and source-timestamp admission (2026-11-01)

**Status: G0 PARTIAL, not accepted for quantitative concentration or conservation-law interpretation.** This document extends the [Drive dataset census](phase0-drive-dataset-census-2026-11-01.md), recording read-only measurements on six authorized original historical .7z archives. The complete scripts, JSON outputs, image subset and SHA-256 manifest are retained on the authorized workstation under `X:\AI-Lab-Test\Solidification_OFV\analysis_outputs\phase0_scout_2026-11-01` (**not** published to the public GitHub repository).

## Archive identity and integrity

The six archives contain 29,025 TIFF *entries*; derived/outlier-removed and cropped duplicates mean this is not the count of independent experiments. All six passed 7-Zip archive listing. **2014-01-15.7z also passed full `7z t` integrity testing**, 2,109 files, exit 0. SHA-256 of that full unchanged archive: `eb418bd6b1f786096703f56b15a9b9281c0c60d419e90fcf24f5349379eca8c9`.

**Important version conflict:** The X: archive `2011-09-09.7z` is **4,954,161,853 bytes**, whereas the similarly named Drive object is **2,846,280,956 bytes**. They are not byte-identical and must be treated as separate versions pending source manifest comparison. Neither the compressed archives nor selected source TIFFs were copied to GitHub.

## Direct repo-source ↔ original-image identification

The repository's [ImagePreprocessWithReference.py](../Python_code/ImagePreprocessWithReference.py) explicitly selects the example input `2011-09-09-Experiment-1` and `Reference` and uses `I_corr=I/I0`, noting that dark-current information is absent **for that example**. The newly accessible 2011-09-09 raw archive contains Exp1, Exp2, outlier-removed derived branches and 214 reference TIFFs. An exactly filtered three-file extraction supplied an original Exp1 frame, its numbered outlier-removed counterpart, and a reference frame.

All three are 758×572, 16-bit grayscale TIFFs. The original vs outlier-removed frame share geometry but have **109,726/433,576 = 25.307% exactly equal pixels**, RMS difference **524.826 raw counts**. This is strong evidence that cleaned and raw source variants are not interchangeable, but does **not** prove which variant was in the historical `Example_input_outputInput` folder. On one raw/reference pair, `I/R>0` for all pixels and median `g=-ln(I/R)=-0.0007536`; numerical validity is **not composition calibration**.

## 2014-01-15: contrast between reference-only and dark-corrected methods

Source archive (760×560, uint16) contains 1,891 experiment frames, 113 reference frames and 105 dark-current frames; five frames spread across each branch were selected. Filename times: reference **10:26:52–10:28:44**, experiment **10:40:24–11:11:57**, dark **11:12:22–11:14:06**. ImageJ TIFF tags independently confirm uint16, dimensions and uncompressed grayscale samples. Original detector counts are read without display normalization.

Using five-frame per-pixel mean dark `D` and reference `R`, the exploratory `(I-D)/(R-D)` ratio is admitted only when both numerator and denominator are positive:

| Experiment position | Valid mask fraction | Fraction `g<0` among valid | Median admitted `g` |
|---|---:|---:|---:|
| First | 0.6983 | 0.5150 | -0.00376 |
| Quarter | 0.6910 | 0.5529 | -0.01452 |
| Middle | 0.5829 | 0.1977 | +0.16302 |
| Three-quarters | 0.4942 | 0.2029 | +0.30642 |
| Last | 0.4049 | 0.2105 | +0.42535 |

Per-pixel **median** R,D produces similar valid fractions (0.6962, 0.6894, 0.5815, 0.4943, 0.4055); this is not explained by one unlucky reference/dark image. Detector mean counts are `~58,200` for the reference and `~55,500–56,000` for dark, with some pixels at 65535; the offset/reference temporal history and chamber mask require investigation.

The same five images with the reference-only `I/R` branch have **100% algebraically positive ratios** and median `g` of -0.00038,-0.00148,+0.01497,+0.03272,+0.06747. This **does not validate** neglecting dark current; the two optical-density definitions are scientifically different. No invalid values were silently clamped, no image was converted to In wt.%, and the Kristofers empirical concentration fit is **not** assumed transferable to 2011–2014 experiments.

## Full source-name timing census

A reproducible standard-library script listed all six archives with installed native 7-Zip, grouped timestamp-encoded original TIFF filenames, and recorded all folder-specific first/last times, positive time intervals, temporal gaps and parsing failures in `raw_timing_census.json`. **Every main experiment with parseable source timestamps shows median adjacent interval 1.000 s**, with some gaps. These are *filename-derived times*, not independently certified instrument clock records.

The historical preprocessor hardcodes `dt0=0.2 s` and `bin_size=5`. Applying this timing to any raw 2011–2014 sequence without verifying the acquisition would introduce a **fivefold temporal-scale mismatch** against the nominal filename spacing. Implement a separate, metadata-driven frame/time-to-OFV-pair-midpoint contract with explicit gap refusal. Do not infer timing from AVI playback rate or filenames alone.

## Security, artifact status and decisions

- Original .7z archives left unchanged. 2014 7-Zip full CRC test passed; other five structurally listed but not fully CRC tested.
- A first attempted 7-Zip selective extraction unintentionally expanded the entire 2014 archive into the *analysis workspace*. Exactly 2,094 unintended **working copies** (1,783,013,132 bytes) were removed after verifying the 15 retained samples. The 2011 extraction used verified `-i!full/path` selectors and retained exactly three samples. Source archives were never modified.
- Scripts and results on X: `radiometric_pilot.py`, `radiometric_multiframe_sensitivity.py`, `radiometric_reference_only_comparator.py`, `source_match_2011.py`, `raw_timing_census.py`, associated JSON files, `WORKSPACE_SHA256_MANIFEST.csv`, and `PHASE0_RAW_RADIOMETRY_FINDINGS_2026-11-01.md`.
- No quantitative `Conc_In` product or wall/crop geometry was established. Historical raw data cannot be paired with the verified March-31-2026 82×98 2WCF output on filenames or dimensions alone. No mechanical energy closure has been attempted.

**Next recommended gates:** reconstruct the historical source variant/reference selection for the 2011 Exp1 example; characterize legitimate detector/illumination and chamber masks for the 2014 dark-current case; accept raw timebase only with camera provenance and nonuniform-gap handling; then generate experiment-matched quantitative composition and OFV data before experimental mass/energy validation.
