# Agent handoff — Phase 0 original raw TIFF radiometry and nominal clock

**Date:** 2026-11-01, Europe/Riga. **Owner authorization:** proceed with raw-data study on X: through Desktop Commander, with unchanged six input archives. **Branch:** `docs/phase0-drive-census-2026-11-01`, draft PR #5, append-only addition.

## New verified evidence

- Remote workstation MB-PC-256, allowed source/output workspace `X:\AI-Lab-Test\Solidification_OFV`; Python 3.14 standard library, 7-Zip 26.02. Six archives list successfully and include 29,025 TIFF entries (some duplicated/derived). `2014-01-15.7z` passes full `7z t` CRC/integrity check at SHA-256 `eb418bd6b1f786096703f56b15a9b9281c0c60d419e90fcf24f5349379eca8c9`.
- Repository `ImagePreprocessWithReference.py` hardcodes source input `2011-09-09-Experiment-1` with `Reference`, `I/I0` normalization and no dark correction. Exact extracted raw/derived/reference 2011 TIFFs are 758×572 uint16; original and derived match in only 25.307% pixels, RMS difference 524.826 detector counts. Which source variant the historical example used remains unverified.
- 2014-01-15 pilot: 15 selected original 760×560 uint16 TIFFs (five each experiment/ref/dark) extracted under analysis outputs. Five-frame mean R and D produce strict-positive `(I-D)/(R-D)` fractions 0.6983, 0.6910, 0.5829, 0.4942, 0.4049 over the experiment; using median R,D produces almost the same. Reference-only I/R has 100% algebraic positives but omits available dark-current, so is not scientifically equivalent. Neither is calibrated In wt.%.
- Six-archive filename clock census: all main experimental sequences with parseable TIFF timestamps have **median adjacent 1.000 s**, with gaps. Repository raw `dt0=0.2 s` is not accepted for these sources absent camera logs, nor is playback `VideoFPS`. Exact clock and source-OFV pair-midpoint alignment remain G0 blockers.
- Local `2011-09-09.7z` 4,954,161,853 B vs Drive same-named object 2,846,280,956 B — distinct versions pending provenance.
- Initially an incorrectly selective 7zip call extracted the full 2014 TIFF list into analysis outputs; 2,094 surplus working copies (1,783,013,132 B) were scoped and deleted, preserving 15 intended samples, all source archives unchanged. The 2011 extraction used verified explicit `-i!internal/path` selectors, three files exactly.

## Durable output

`X:\AI-Lab-Test\Solidification_OFV\analysis_outputs\phase0_scout_2026-11-01`

Contains: `RAW_ARCHIVE_CENSUS_2026-11-01.md`, `PHASE0_RAW_RADIOMETRY_FINDINGS_2026-11-01.md`, 5 independent standard-library Python analysis scripts, 5 JSON outputs, 18 source TIFF samples, and `WORKSPACE_SHA256_MANIFEST.csv` (31 files, excluding manifest). Raw .7z archives are in the separate raw_archives folder and are not stored in this public repo.

Full numeric evidence in `docs/phase0-historical-raw-radiometry-2026-11-01.md` on this branch.

## Scientific gate

**G0 remains PARTIAL**: exact source provenance and raw timing are not yet certified; original reference/dark behavior is not calibrated, physical crop/wall mask and indium mass-fraction mapping unverified, no same-run quantitative `Conc_In`/OFV data matched. Do not infer 2026 processed experiment identity from raw 2011-2014 labels. Next: identify historical reference/crop/source variant, audit instrument temporal/dark stability, and develop separately versioned pair-center time registration tests. Preserve image x-right/y-down during interpolation and physical y-up for integrals.

This handoff supplements all prior append-only files and does not change scientific production code.
