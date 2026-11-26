# Phase 0 — 2014-04-04 full original-source timeline and native v25 MIL-method admission

**2026-11-11.** Owner-approved development continuation; output remains **experimental diagnostic, not physical G0 acceptance**. Public code is in the companion Python and Wolfram scripts; all 3,557 original TIFFs and their derived image data remain on private, authorized X:. No research data redistribution rights are asserted.

## 1. Generalized source role: Reference = flat field

Owner explicitly confirmed: in *all raw radiography archives/image sequences*, the folder named Reference contains acquisitions recorded for **flat-field correction**. It is not, by virtue of its filename, the initial homogeneous Ga–25 wt.% In sample-image baseline. Preserve three distinct roles:

- R(x,y): measured/reference flat-field detector recording, with source identity, exposure, beam spatial validity and temporal drift checks.
- D(x,y): measured dark/offset if actually available; not inferred by assuming a zero dark image.
- J0(x,y): independently established homogeneous all-liquid *sample* image after appropriate flat-field/dark correction, before solidification and segregation. This is the 25 wt.% In, P=0 composition reference in Shevchenko's method.

Therefore negative-log raw flat-field ratio -ln(I/R) is a potentially useful *diagnostic* attenuation-like signal, but **not** the composition-relative P=-ln(Jt/J0). The reference-only pilot must not silently be relabelled as C_In or validated phase contrast. The user clarification applies to other raw archives as well as this case.

## 2. Verified private full-source evidence

Source: X:\AI-Lab-Test\Solidification_OFV\raw_archives\2014-04-04.7z

Full archive SHA-256: 77fac9a38a9cdaa41ee5ec9c9562acb7149ee1cee8f0246a80c2b267928f2510. Earlier PR #16 established the archive member counts and created SHA-checked per-frame inventory. Source video/clock are not treated as independently measured based only on filenames.

For this development increment, the original 7z remained unchanged. The main and end TIFFs were extracted only into a private analysis workspace, verified against original source member **size and CRC32** and independently decoded as 426×761 unsigned 16-bit grayscale.

- Reference flat field: **111 of 111** original TIFFs CRC checked, first 80 used for a provisional pixelwise median R, last 31 kept as a held-out flat-field stability check.
- Original experiment: **3,446 of 3,446** source TIFFs CRC checked and decoded (main 3,148, end 298).
- Candidate detector-valid pixels: positive and below 65535 in every reference exposure; excludes ~2.12% ever-saturated reference pixels. This is **not** an accepted physical liquid/chamber ROI.
- Descriptive full-field mean negative log(I/R) (per the provisional R) increases as dendritic features appear, but should not be assigned a concentration or interpreted as a phase fraction without sample boundaries and radiometric provenance.

### Strict candidate filename-clock segments

| Group | Stream | Source count | Gap preceding group |
|---|---|---:|---:|
| 1 | main | 919 | start |
| 2 | main | 917 | 4.360 s |
| 3 | main | 934 | 4.359 s |
| 4 | main | 378 | 3.813 s |
| 5 | end | 298 | 177.397 s |

All timing is provisional until the camera clock is independently verified. Do **not** take finite differences, fit temporal derivatives or produce OFV pair assignments across gaps on ordinal frame numbering.

New production-independent source preflight: Python_code/phase0_2014_04_04_fullsource_timeline.py. Its source CRC test is *per member*; this does not assert chemical identity or external camera calibration. It demands the owner-confirmed flat-field provenance and reports conservative acceptance flags. New negative and positive synthetic tests: tests/test_phase0_2014_04_04_fullsource_timeline.py.

## 3. Exact notebook source identity and native method-form smoke test

The read-only historical reference notebook copied to the authorized workstation was independently compared with GitHub's current Mathematica_code/Dendrite & Plume Analysis v25.nb; **both had the identical Git blob SHA b13ef6adda22405d89680e3ebe5da50e6f40d297**. No notebook initialization or saved executable cells were run during inspection.

The extracted v25 mathematical method is:

- flatFieldCorrect[image, flatField] = ImageMultiply[image, flatField^-1]
- getMILseries[image] = Mean @ ColorNegate @ ImageAdjust @ GaussianFilter[flatFieldCorrect[image, referenceFrame], gaussianKernelScale]

For this new 2014-04-04 source, the 80-frame flat-field median was exported as a normalized float32 TIFF. Mathematica 12.1.1 for Windows evaluated the form directly with Gaussian kernel scale **0** on six CRC-verified original images, and all results were finite:

| Frame | Native v25-form MIL (candidate R80) |
|---|---:|
| Main first, 10:25:47.069 | 0.391844422129 |
| Main before first gap, 10:41:05.056 | 0.415005159733 |
| Main after first gap, 10:41:09.416 | 0.410972611781 |
| Main last, 11:18:23.600 | 0.465078028201 |
| End first, 11:21:20.997 | 0.421012457325 |
| End last, 11:26:18.009 | 0.413401668453 |

The new checked-in sample tool is Mathematica_code/Phase0_2014_04_04_Native_MIL_Method_Probe.wls; it reads a JSON config giving R80, individual source TIFFs and an output path. On Windows native Mathematica 12.1.1 it reproduced the earlier private numerical probe **exactly across all six values**.

**Critical boundary:** this verifies the notebook's MIL *formula and runtime* with new source frames. It does **not** prove the original historical 2014-04-04 notebook run, preprocessing/crop, original R, segment selection, valid chamber ROI, case-specific dynamic threshold parameters, binary mask equivalence, or experimental chemical calibration. In particular the native output is neither a solid-area fraction nor indium wt.%. No accepted direct threshold/segmentation-mask comparison is yet possible.

## 4. Private artifacts and reproducibility

Private execution root:
X:\AI-Lab-Test\Solidification_OFV\analysis_outputs\phase0_2014-04-04_fullsource_preflight_2026-11-11

Verified outputs, with private SHA256:
- fullsource_timeline_repo_verified.json — AF4AD05666F05CE3F2BA9BD3C988E2FD023BCDDD2AFAEDA2366059BA0814D0A8
- fullsource_timeline_repo_verified.csv — B0DA3BB4588E37A4A92EC5C02B37E94086CB1F5A7B25C915156E53CA4F6998B8
- native_mil_method_repo_probe_v1.json — 4D7955F67B4B365A84278C4D4C350D2074CCB70AE8EFB89E1994CC26C59E1152
- Corrected temporal figure: full_3446_temporal_flatfield_preview_v2.png — F5002DAAB4BA56643B00469B01247CFE508E19B54B5AB0AB3A174C796CDDA7B6

The first exploratory plotting script put vertical break markers at incorrect absolute-clock positions. Its plot is retained **only as a rejected draft**; the V2 plot corrects the x-coordinate normalization and records this correction in temporal_plot_v2_qa.json. The numerical frame table was unaffected.

**Validation:** Ten new synthetic Python tests passed on native Windows Python 3.10 with NumPy and tifffile; the full 3,446-frame source-run was independently performed using the checked-in module, not only an earlier private prototype. CI without these optional science packages may SKIP the image tests. Native Wolfram is a separate acceptance level from CI.

## 5. Next experiments and stopping conditions

1. Expert review and independent annotations of the actual **chamber/sample boundaries, valid detector region, liquid/solid mask and first-solidification time**. The stored preview images show morphology but do not independently certify ROI geometry, real phase occupancy or full-thickness dendrites.
2. Recover or independently constrain 2014-04-04 camera exposure/clock, beam/detector flat-field spatial response and any measured D. Establish that the flat-field and experimental images correspond to a shared detector geometry; equal 761×426 shape alone is not a pixel registration.
3. Identify **separate all-liquid pre-cooling sample frames** and validate their homogeneous 25 wt.% In composition before constructing J0 and an absolute P=0 calibration.
4. Only after source/ROI identity is accepted, run actual full-series v25 temporal MIL and source-fidelity image filtering with *case-specific* parameters; compare masks with held-out independently annotated solid masks, not retrospective algorithm masks alone.
5. Then perform liquid-only KMedoids and coherent plume core tracking on accepted source regions. A cluster rank is not a 5–10 wt.% concentration label. Dendrite ~98.6 wt.% requires independent evidence for full beam-thickness filling.
6. Keep 2014-03-07 historical cropped 567×276 image versus 763×384 mask registration **unresolved**. Do not resize or pair by ordinal name alone. Likewise OFV PKL source/time/crop registration remains G0-blocked.

**No change to user raw archive, original notebook, pre-existing PR #14 OFV numerical code, or previously produced masks. G0 remains OPEN.**
