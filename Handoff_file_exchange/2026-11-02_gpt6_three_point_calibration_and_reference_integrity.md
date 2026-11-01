# Agent handoff supplement — three-point Ga–In calibration source and averaged-TIFF integrity finding

**Date:** 2026-11-02 (Europe/Riga). **Branch:** `feat/phase0-timestamp-registration-2026-11-02`, proposed draft PR #6. This is append-only and does not alter the initial 2026-11-02 handoff.

## Recovered methodological source

Located `Concentration_mapping_intermediate.docx` (Natalia Shevchenko, HZDR) among accessible Project files. It defines `P=-ln(I/I0)` with **dark-current-corrected** reference and experimental radiographs; `C0=25 wt.% In` at `P=0`; indium-rich `C≈98.6 wt.% In` from selected dendrites *assuming full X-ray depth span*; Ga-rich channel `C≈5–10 wt.% In`, independently supported by a gallium-filled cell. These three anchors are used for **semi-quantitative** calibration. No actual `P` coordinates, channel/solid spatial masks or fit covariance for this historical 2014 case has been verified; do NOT reuse Natalia's or Kristofers' final fitted coefficients without matched source conditions.

Published related article: Birjukovs, Shevchenko and Eckert, *Experiments in Fluids* **64:131 (2023)**, DOI `10.1007/s00348-023-03671-2`. Experimental methods state a 35×25×0.15 mm Hele–Shaw cell imaged at 1 fps with 1-second exposure, typical ~760×576 grayscale 16-bit TIFF, dataset-dependent pixel size about 13.7–37.6 µm. This **supports** the six historical filename-sequence 1-s nominal spacing but is not archive-specific camera metadata or crop geometry. Article Algorithm 9: MIL/solid-front based liquid sampling (median, bilateral and non-local filtering) with *optional* Beer–Lambert conversion. Algorithm 10: solid/LZ masks plus 15-px front buffer, filtering, K-medoids luminance levels ranked for plume segmentation; this is distinct from physical concentration calibration. Notebook `Dendrite & Plume Analysis v25.nb` implements related machinery and was reviewed as inert Notebook data with WolframScript, not blindly executed.

## Newly tested historical average-vs-raw discrepancy

Archive `2014-04-15-Exp2.7z` contains TIFFs labelled `ga-25in-ref2.txt, Averaged.tif` and `ga-25in-dark2.txt, Averaged.tif`. A selective 7-Zip extraction with full-path includes retained exactly two experimental original TIFFs, those averaged TIFFs, then one actual original individual reference and dark TIFF (all 762×499 uint16). Original archive was unchanged.

- Averaged reference mean **28,717.72** counts; one original reference **57,831.93**. Median pointwise average/single ratio **0.3766**.
- Averaged dark mean **28,329.15**; one original dark **52,182.13**. Median pointwise ratio **0.4071**. This is **not** proven to be simple 0.5 scaling.
- First experimental frame: archived-average based dark correction valid **62.33%**, median `g=-1.5674`; individual-original based dark correction valid **79.76%**, median `g=+0.00149`.
- Last experimental frame: archived-average based valid **61.71%**, median `g=-1.4832`; individual-original based valid **60.48%**, median `g=+0.45867`.
- Individual-reference-only `I/R` medians `g=+0.00054` first and `g=+0.06022` last.
- All are **uncalibrated diagnostics**, and an individual reference/dark exposure is not an accepted reference model. Original averaging/export/provenance and field mask require investigation before trust.

Scripts and JSON preserved in authorized X: folder `analysis_outputs\phase0_scout_2026-11-01`, filenames `radiometric_2014_04_15_pilot.*`, `audit_imagej_average_2014_04_15.py`, `imagej_average_integrity_2014_04_15.json`, `radiometric_2014_04_15_individual.*`. See `docs/phase0-plume-segmentation-timing-g0-2026-11-02.md` for public derived numbers.

**G0 still open**. No actual acquisition-specific calibration values, verified solid/plume/bulk masks, raw-to-OFV mapping, local full-wall crop calibration or quantitative mass/energy validation has been accepted. Preserve image x-right/y-down reconstruction, physical +z curl and explicit pair-center association.
