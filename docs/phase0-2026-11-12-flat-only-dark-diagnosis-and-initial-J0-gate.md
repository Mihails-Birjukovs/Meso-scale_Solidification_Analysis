# Phase 0 — flat-only working default, dark-current forensic diagnosis and 2014-04-04 specimen J0 gate

**Date:** 2026-11-12 (Europe/Riga). **Scientific state:** source-backed diagnostic and safeguarded development; **no chemical concentration G0, physical ROI, source camera time, MIL mask or initial melt homogeneity admitted**. This report extends merged PR #16, draft PR #18 and GitHub Issues #11 and #17.

## Decision: flat-only working default; dark branch isolated

Owner confirmed that all raw-sequence `Reference` folders are recordings for **detector flat-field correction**. Accordingly the default preparatory branch is measured `I/R_flat` on positive, unsaturated, source-matched pixels. This is a **working algorithmic default** for source image preparation, MIL candidate segmentation and exploratory flow diagnostics; it is NOT a claim of physically exact X-ray absorption in the presence of a nonzero detector offset.

**Do not automatically subtract files named Dark Current.** Allow dark-corrected `(I-D)/(R-D)` only as an explicitly flagged *diagnostic* branch until the independently verified source, shutter/beam-off condition, exposure/gain/temperature compatibility, temporal stability, chamber spatial ROI, and safe strictly positive source signal conditions are all satisfied. No arbitrary `epsilon`, absolute value, zero fill or clipping may convert a physically nonpositive photon signal into valid attenuation. Dark current images must be preserved as raw evidence, never discarded.

**Separate specimen composition baseline.** For an independently verified homogeneous pre-cooling Ga–25 wt.% In initial liquid, the sample-radiometry baseline is `J0=(I_initial-D)/(R-D)` if D is validated, or provisional `J0=I_initial/R` in flat-only mode. The composition-relative target is `P=-ln(Jt/J0)`, not automatically the diagnostic `-ln(I/R)`. When the same R applies and D is not subtracted, `P_candidate=-ln(I_t/I_initial)` numerically, but its absolute physical interpretation remains biased by any unknown additive detector pedestal. This is not chemical calibration.

## Direct archived-image evidence (source scout 2026-11-01, independently reinspected 2026-11-12)

Native reference/dark mean fields came from reconstructed *original single-frame uint16 stacks* in `X:\AI-Lab-Test\Solidification_OFV\analysis_outputs\phase0_scout_2026-11-01`. Two case-specific spatial comparisons retained original 760×560 (`2014-01-15`) and 762×499 (`2014-04-15-Exp2`) detector grids, not arbitrary resized masks. A central 200×200 candidate patch used x=[280,480), y=[180,380); this patch is **not** an expert-validated sample region.

| Evidence | 2014-01-15 | 2014-04-15-Exp2 |
|---|---:|---:|
| Flat field source TIFF count | 113 | 108 |
| Labelled dark source TIFF count | 105 | 120 |
| Flat-field frame-mean peak-to-peak range | 78.22 counts | 82.89 counts |
| Dark frame-mean peak-to-peak range | 2,293.78 counts | 3,781.46 counts |
| Dark range / ensemble-mean (R-D) | 86.95% | 107.14% |
| Full positive raw-count pixel subset with R<=D | 27.70% | 22.78% |
| Central candidate 200×200 with R<=D | 0.005% | 0.0325% |
| Whole-field spatial Pearson corr(R,D) | −0.0227 | −0.0977 |
| Candidate central spatial Pearson corr(R,D) | +0.1210 | +0.1202 |

The mean image labelled D has a much flatter but vertically striped spatial pattern than R, not the same beam-illumination profile. This does **not prove** the dark acquisition is mislabeled; it is compatible with a high digital pedestal and distinct dark fixed-pattern response, but shutter, camera mode and offset provenance are unverified. R-D is mostly positive in the central bright region, while it is nonpositive over large peripheral detector areas. The sample can also fall below D in later dark-corrected frames, notably near solid material. Algebraic positivity inside a patch is necessary, but not evidence that D is the correct offset during the earlier sample acquisition.

Archived exploratory dark-subtracted `-ln((I-D)/(R-D))` differs strongly in median, distribution and nine-level KMedoids map from flat-only `-ln(I/R)`. In the reconstruction's central 200×200 patch, 2014-04-15 Exp2 dark-corrected valid fraction was 99.965% for the first inspected sample but only 74.43% for a late sample; 2014-01-15 early 99.9925%, late 88.1875%. Unmatched rejected pixels and the change of signal meaning invalidate direct mode-swapping comparisons.

**Independent archived-average problem:** `ga-25in-ref2.txt, Averaged.tif` mean 28,717.7 and `ga-25in-dark2.txt, Averaged.tif` mean 28,329.1, against original individual ref/dark means ~57,832 and ~52,182. The median per-pixel archived-average/single ratio was 0.3766 and 0.4071, respectively: not a constant 1/2 transform. These files have unverified averaging/export intensity semantics; exclude them from raw detector-count correction unless their provenance and numeric transform can be recovered.

### Primary local evidence files and SHA-256

- Dark R/D spatial-test JSON: `X:\AI-Lab-Test\Solidification_OFV\analysis_outputs\phase0_dark_diagnosis_2026-11-12\background_spatial_test.json` — `B9277F80D6404AF07D1B10C3597ABE79A1D3AC9EAB51E3B015EF9D2F3BCE4445`.
- Source ensemble frame-mean trace JSON: `reference_vs_dark_stack_mean_trace.json` — `6EEC9207873C54086C5A0DE89469F7CB71DEA7E9D9829B252B17B673F3044FC6`.
- Spatial montage: `two_archives_flat_vs_dark_spatial.png` — `CBC0A19CCD6E89330498546D8507197ED253E63A52BC414B43D604123EDA3614`.
- Drift figure: `reference_vs_dark_stack_mean_trace.png` — `21E525AA0B939E6C34E01305C0AF16480528F76CCACF56F8E5F5974C4DDAD95A`.

## 2014-04-04 early specimen J0 candidate and first-growth screening

Original archive SHA256 `77fac9a38a9cdaa41ee5ec9c9562acb7149ee1cee8f0246a80c2b267928f2510`; 111 reference flat-field TIFFs and 3,446 sample TIFFs were previously source CRC matched in private X: as part of draft PR #18. Original image geometry: **426 rows ×761 columns**, origin at upper left with x right/y down. No expert-approved chamber polygons. Candidate central ROI x=[260,650), y=[165,350) excludes visually prominent peripheral detector obstructions but is NOT independently phase- or chamber-validated.

Provisional J0: pixelwise median of **main experimental source TIFF ordinals 0–79** (not Reference folder). Hold out **80–119** in the same uninterrupted filename-time segment. On accepted source pixel positivity/saturation only, the maximum absolute held-out *frame median* `-ln(I_t/J0_candidate)` in the central ROI was **0.0008704124**. End of main sequence ordinal 3147 has central-region median diagnostic signal **+0.03126**, substantially larger. This supports baseline **stability**, not initial chemical homogeneity or phase identity.

Exploratory lower-band onset detection uses x=[185,650), y=[345,405) and a threshold |P_candidate|>0.04 sustained above a fraction of pixels for 20 consecutive frames. Candidate first sustained changes: 0.1% => **ordinal 480 / 10:33:47.065**, 1% => **ordinal 565 / 10:35:12.067**, 5% => **ordinal 639 / 10:36:26.053**. These are *not* independent first-solidification observations, native v25 MIL or certified timestamps. Detection thresholds/ROI were post-hoc exploratory and must be pre-registered before independent confirmation.

New source verifier: `Python_code/phase0_2014_04_04_provisional_sample_baseline.py`. It requires the exact SHA-verified archive inventory, checks CRC32 for each selected original TIFF, rejects an initial train/holdout window with gaps >1.5 s, prohibits invalid ROI/case geometry, and always emits `initial_25wtpct_composition_verified=false`, `independent_expert_phase_and_ROI_review=false`. Portable scalar-gate code: `Python_code/phase0_radiometry_branch_contract.py`; production code computes no new dark corrected values.

Private source visual/metric outputs:
- Candidate baseline JSON: `X:\AI-Lab-Test\Solidification_OFV\analysis_outputs\phase0_initial_baseline_gate_2026-11-12\provisional_J0_repo_probe_v1.json`, SHA256 `9A1F16F044E823A13DA7E88918615D5976F5B2949C6C8A2D7F5F2138831414C8`.
- First/late onset screen: `early_baseline_onset_preview_candidate.png`, SHA256 `6FD9EE897744EC8D9393B93D79D0F2DD869F50BA383D31C5FD0746744EE320D5`.
- Onset candidate manifest: `early_baseline_lower_band_onset_manifest.json`, SHA256 `AEDC7F6AECE7B41E0DFF3B7369CB158602E165E83961F53577FD68E9475D667E`.
- All-main-frame ROI onset trace: `early_baseline_lower_band_onset_source_trace.csv`, SHA256 `987FCDEEAA244B7DE9BD93D268234A145FE3117563847A8E39BED74833EF7D11`.

## Acceptance decisions and immediate next evidence

1. **Working processing default ACCEPT as exploratory:** original measured R flat-only normalization; correct legacy `I/I0` labels and output metadata, but do NOT alter pixel math or overwrite old outputs.
2. **Dark-corrected quantitative branch BLOCK:** require original detector dark shutter status, gain/exposure match, thermal/temporal characterization, valid source-matched ROI and signal-above-offset across all intended frames; preserve rejected pixels as missing data.
3. **Candidate initial specimen baseline ACCEPT as exploratory only:** repeat first/last early-frame shape/registration, review whether source frames 0–79 are truly homogeneous liquid and before cooling, review sample ROI/walls on original images; physical 25wt% baseline still BLOCKED.
4. **Independent ROI/solid annotation BLOCK:** use `X:\AI-Lab-Test\Solidification_OFV\analysis_outputs\phase0_2014-04-04_fullsource_preflight_2026-11-11\2014-04-04_unlabelled_coordinate_review_sheet_v1.png` and `2014-04-04_roi_annotation_TEMPLATE_unreviewed_v1.json`, register reviewer and source frame IDs. Candidate rectangles are not automatically expert accepted.
5. **MIL, plume, absolute C_In, OFV and G0 closure BLOCK:** full source-specific preprocessing, experimentally matched masks and verified endpoints, clocks and physics remain essential. Preserve 2014-03-07 cropped 567×276 versus historical 763×384 mask registration as separate unresolved geometry gate.

**Safety:** Raw research archives, historical masks, Mathematica master notebook and PR #18 untouched. Changes in this PR are conservative source semantics, new diagnostics/tests and metadata only. Scientific libraries are not assumed installed by CI; native Windows Python 3.10 checks are reported separately.
