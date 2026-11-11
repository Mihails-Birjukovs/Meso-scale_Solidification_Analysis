# Phase 0 — 2014-04-04 raw Ga–In archive admission

**Date:** 2026-11-11. **Evidence:** owner's authorized private X: source, read-only 7-Zip 26.02 metadata listing and independent full-archive SHA-256. **State:** header and filenames inspected; no TIFF pixel data, calibration anchors, camera clock or solid-liquid masks scientifically admitted.

## 1. Source archive and three distinct acquisition streams

Private source path: X:\AI-Lab-Test\Solidification_OFV\raw_archives\2014-04-04.7z

- Size: **1,507,471,570 bytes**. SHA-256: **77fac9a38a9cdaa41ee5ec9c9562acb7149ee1cee8f0246a80c2b267928f2510** (independently read and hashed on the authorized X: workstation).
- Native listing: **3,558 files** (3,557 TIFF and one Thumbs.db), 3 folders, solid LZMA2 archive, 2 compression blocks. This is a **header census**, not a 7z member CRC integrity check.
- **Flat-field Reference recording (owner-confirmed):** 111 TIFF, folder 2014-04-04/Reference, prefix ga-25in-ref1, filename times 10:07:43.889–10:09:33.879.
- **Main:** 3,148 TIFF, folder 2014-04-04/2014-04-04, prefix ga-25in-1, filename times 10:25:47.069–11:18:23.600.
- **End:** 298 TIFF in same experimental folder, prefix ga-25in-end1, filename times 11:21:20.997–11:26:18.009.
- Filename-based gap from last reference to first main frame: **973.190 s**. Last main to first end frame: **177.397 s**. Do not interpolate across segment gaps or presume uninterrupted optical-flow pairs.
- Observed member sizes were around 648,658 bytes (experiment) and 648,664 bytes (reference); actual image dimensions, pixel values and TIFF codecs are pending independent decode.

## 2. Admission utility and evidence limits

New: Python_code/phase0_2014_04_04_archive_admission.py, tests/test_phase0_2014_04_04_archive_admission.py, and docs/phase0_calibration_cases/2014-04-04.case.json.

The utility invokes installed 7z with a fixed argument array to retrieve the technical file listing, without extraction or executing archive members. It checks unencrypted metadata, safe member paths, precise role, prefix, count and case-date constraints, CRC metadata presence and plausible filename times. It verifies the archive's full SHA-256 by streaming it read-only, unless asked to produce a clearly weaker no-hash diagnostic. It refuses to overwrite an existing output.

Report deliberately leaves **physical clock, homogeneous-liquid baseline, original TIFF pixel decoding, member CRC verification, dark correction, image registration and absolute C_In calibration all false**. The owner confirms Reference folders across the raw archives are flat-field acquisitions. They are not homogeneous-liquid sample baselines; a separate initial sample reference is required for the Shevchenko P=0 at 25 wt.% In.

Windows CLI usage (from the repository root):

    python Python_code/phase0_2014_04_04_archive_admission.py --archive "X:\AI-Lab-Test\Solidification_OFV\raw_archives\2014-04-04.7z" --case "docs/phase0_calibration_cases/2014-04-04.case.json" --seven-zip "C:\Program Files\7-Zip\7z.exe" --output "X:\AI-Lab-Test\Solidification_OFV\analysis_outputs\phase0_2014-04-04_archive_admission_2026-11-11\inventory.json"

Keep source data and full read-only result on private X:. Do not put TIFF/PNG data on public GitHub without redistribution authorization.

## 3. Dual-case roles and scientific acceptance gates

| Requirement | 2014-03-07 | 2014-04-04 |
|---|---|---|
| Strongest input evidence | 500 processed TIFFs and 418 algorithmic masks with private SHA inventory | SHA-identified original 7z archive with 3,446 experiment and 111 reference TIFFs |
| Geometry | 567×276 images versus 763×384 masks; evaluated crop transform unknown | Original TIFF geometry, pixel coordinate origin and detector validity masks not yet checked |
| Temporal mapping | 418 historical source IDs, no source camera clock accepted | Candidate filename times, three stream segments with gaps; camera clock not certified |
| Radiometry | Original flat/reference and dark not found | Flat-field recording confirmed by owner; spatial flat/exposure quality and measured dark not yet verified; sample I0 missing |
| Morphology | Reconstruct temporal MIL, compare historical masks only after registration | Apply source-faithful MIL to original frame sequence with segment-specific holdouts |
| Absolute chemical calibration | Blocked | Blocked; 25/98.6/5–10 wt.% are hypotheses requiring independent physical evidence |

### Next experimental stages

1. **Pixel integrity and provenance:** sample TIFFs from first/middle/last positions in each stream, record geometry, pixel type, value distributions, exposure metadata and independent decoded pixel checks; separately run native archive CRC check if justified.
2. **Flat-field suitability:** quantify 111 flat-field reference-frame spatial patterns, temporal drift, saturation, valid detector regions and beam/exposure comparability. Independently locate actual pre-solidification all-liquid sample frames for composition baseline. Reserve a nonoverlapping reference holdout interval.
3. **Radiometry:** retain measured uint16 counts; use owner-confirmed Reference folders as measured beam/reference flat-field R (subject to validation), never as the pre-solidification sample composition reference J0. Dark-corrected (I-D)/(R-D) requires a measured dark frame; otherwise keep no-dark reference-only analysis as provisional and explicitly label it.
4. **MIL/dendrites/plumes:** use case-specific empirical parameters, independent solid-boundary annotations and liquid-only plume segmentation. Use K={9,12,16,24,32} and filtering controls. Original unfiltered optical density, not display intensity or cluster labels, is the measured anchor candidate signal.
5. **Calibrated concentration:** 25 wt.% only for verified pre-solidification homogeneous liquid; 98.6 wt.% only for plausibly full-thickness coarsened dendrites; 5–10 wt.% only for independently supported Ga-rich melt channels. Avoid treating arbitrary darkest/brightest pixels or plume cores as endpoints. Consider solid-versus-liquid attenuation/path-length differences and blocked spatial/temporal validation.
6. **G0 OFV:** source-matched PKL sample, VelocityInversion, physical pixel pitch, image bins and pair midpoint clock required before velocities/concentrations become a common experiment result.

Do not transplant 2020 MIL parameters into either 2014 case by default. The v25 notebook is methodological authority, and its actual evaluated case-specific settings need checking.

**Scope:** this PR changes no original notebook, raw frame, production OFV processor or calibration script; PRs #14/#15 remain separate drafts; Issues #9–#12 remain OPEN. Source inventory is not physical calibration acceptance.
