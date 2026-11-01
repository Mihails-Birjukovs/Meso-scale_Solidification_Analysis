# Additional Phase-0 research-agent handoff — original archived 2WCF output recovered

**Date:** 2026-11-01 (Europe/Riga)  
**Agent ID:** ChatGPT-GPT-6 / Solidification OFV Phase 0  
**Branch:** `fix/ofv-coordinate-signs-phase0-2026-11-01`; **draft PR #3**.  
**Policy:** Append-only supplement; the earlier `2026-11-01_gpt6_phase0_representative_image_and_coordinate_handoff.md` must remain unchanged.

## New source and read-only inspection

Identified a matching-by-filename original 2WCF-SVD output archive in the owner's connected Drive, item ID `1A7fBi_jZDlzHCoZvJAjPXFP3O0ngusjn`:
`20260331_4 Downsampled ImagesRun1_20260331_v3_3D_filtered_enhanced_KLD_v2_Run1_run_2.7z`. This is separate from the 80-frame input-image archive, ID `1tnxbxv2BI5F0RDWF0oF3mBI7YPfsq3l-`.

Archive inspected with a local archive library. Contents: 79 `velocity_field_00000..00078.pkl`, 79 corresponding WXF files, 79-row `flow_qc_metrics.csv`, `parameters.json`, parameters CSV, QC plot and AVI. All 79 NumPy pickle records were inspected using an explicitly restricted allowed-global unpickler (not unrestricted `pickle.load`); every record has finite 1D x/y/u/v arrays of equal length, and sample grid x and y indices are 1 modulo 3.

The **actual archived run parameters** differ from the pinned upstream script's current defaults: `USE_SVD=true`, `KillIDs=[0]`, `ArrowDensityStep=3`, `MedianOfMeansGroupSize=1000`, `VelocityInversion=-1`, `UseConfidenceSmoothing=true`, `ConfidenceSigma=5`, `ConfidenceKernelSize=5`, `MinConfidence=0.01`, plus the documented Farnebäck parameters. `VideoFPS=5` describes playback and should **not** be treated as verified actual experiment frame rate.

Original output diagnostics: 576–891 sparse vectors per frame pair, median 852; median pair apparent speed 0.8912318 px/pair; median forward/backward QC error 0.1191106 px. The archived output supplies real upstream-format vectors and QC, but no commit hash or input acquisition manifest. It cannot certify the exact upstream generating commit, frame timing, geometric calibration, concentration synchronization or physical wall positions. The original program was **not re-executed**.

## User-visible and repo artifacts

- Detailed numeric methodology and both source-matched test results and actual saved-output audit: `docs/phase0-representative-sequence-2026-11-01.md` (updated on draft PR #3).
- Draft PR #3 body updated to refer to new original-output evidence.
- No raw images, PKLs or third-party upstream implementation were uploaded to this public repo.
- Source correction remains deliberately narrow: undo both saved component inversions for image-grid interpolation, remove vertical-only flip, and correct the physical vorticity sign.

## What remains

Gate G0 is not passed. Need a true original 2WCF re-execution pinned to a known commit/environment, with exact TIFF image provenance and run params (including SVD); confirm actual source acquisition period, crop offset, calibrated `Conc_In` image sequence and output time alignment. Need a full integration run of the modified postprocessor against correctly paired **same-acquisition** concentration data before interpreting derived fields. Do not silently transpose or change height/coordinate conventions.

This new handoff adds evidence without retroactively editing prior append-only agent handoffs.
