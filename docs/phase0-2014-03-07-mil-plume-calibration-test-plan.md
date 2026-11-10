# 2014-03-07 — registered MIL/segmentation-assisted calibration benchmark

**Case ID:** `2014-03-07`. **Evidence:** actual original images/masks present on the owner's authorized X: workspace, not publicly redistributable in this PR. **Status:** source inventory and format checks PASS, spatial correspondence and concentration-calibration gates BLOCKED. **Methodological source:** `Mathematica_code/Dendrite & Plume Analysis v25.nb`; it records **37.6 µm/pixel and 1-second exposure** for the 2014-03-07 series. These values do not independently prove source camera timestamps, dark/background correction, physical crop or reconstruction scale.

## 1. Case inputs from the owner's archived examples

| Source role | Contents | Format checked | Status |
|---|---|---|---|
| `1 Cropped Images` | 500 contiguous `Frame_1.tiff`…`Frame_500.tiff` | 567×276, unsigned 16-bit, **old-style Deflate TIFF compression tag 32946** | PASS for inventory and metadata only |
| `Solid Domain Masks` | 418 contiguous `Frame_1.png`…`Frame_418.png` | 763×384, grayscale 1-bit PNG, binary pixels 0/255 | PASS for inventory and metadata only |
| `Selected Frame IDs.csv` | 418 exact IDs 600,605,…,2685 | step=5, one ID per line | PASS for IDs; image–mask association NOT YET verified |
| Original 2014-03-07 acquisition radiographs / flat-field / dark series | Not identified in the six original raw 7z archives or this example folder | — | BLOCKED; no implied reference correction |
| Original case-specific `(P,C_{In})` chemical reference measurements | Not verified | — | BLOCKED |

The 2014-03-07 **cropped-image domain and historical solid-mask domain have different shapes and could represent different fields of view or preprocessing geometries**, not a simple known isotropic scaling. Until original notebook crop and selection metadata establish a proper transform, **do not resize or register them by shape alone**, calculate Dice, or reuse the binary historical solid mask as a mask on the cropped image. Even after registration, the old generated masks are comparison outputs, not independent ground truth.

The exact repository case specification is [`2014-03-07.case.json`](phase0_calibration_cases/2014-03-07.case.json). It binds file counts, relative path roles, source-frame sequence, format expectations, candidate K-values and explicitly missing scientific anchors. The companion [`phase0_2014_03_07_case_admission.py`](../Python_code/phase0_2014_03_07_case_admission.py) reads original file headers and hashes **all 918 input files without modifying them**, writes a manifest, and deliberately returns `mask_iou_admitted=false` and `physical_concentration_curve_admitted=false`. [Unit tests](../tests/test_phase0_2014_03_07_case_admission.py) use synthetic TIFF/PNG fixtures and assert this scientific refusal behavior.

An executed test on the authorized X: originals produced:
- Inventory **500 TIFF + 418 PNG**, **418 IDs 600…2685**, no filename/index gaps.
- Source TIFF **567×276**, `Bit16`, compression tag **32946**; historical mask **763×384**, 1-bit grayscale, binary mask.
- `2014-03-07_full_source_inventory.json`: **151335 bytes**, SHA-256 **`63dc854162b5d928d187689e1e34e983b0774c915b43eb7e8fdd216dcb370338`**. It records each input filename, byte size, SHA-256 and current refusal state. That output is **private**, not a GitHub fixture download.
- Independent local Mathematica decoding of selected frames 1,100,300,418 agrees on geometry and 16-bit sample type. `ImageData[..., "Real32"]` values on those *processed* crops were in the approximate ranges 0.52–0.97. This normalized array representation is **not proof of a directly calibrated optical density or raw detector-count transform**.

## 2. Scientific test matrix: solid and convective plume segmentation

**Admission G0-A — time and crop:** Recover and verify which camera frames and original cropped pixel coordinates generated `Frame_j.tiff` and `Frame_j.png`. Confirm why the image set has 500 frames and mask set 418, and whether the 418 source IDs apply to both. Require an explicit source/crop/resize transform, preferably through notebook cell history/source preprocessing parameters. No pixelwise comparison until accepted.

**Admission G0-B — radiometry:** Determine whether the processed TIFF intensity is raw `I`, reference ratio `I/I_0`, optical density `P=-ln(I/I_0)`, or another enhancement result. Reconstruct appropriate beam/reference and dark sequences if original ones are recoverable. Keep a reference-only branch; retain dark-corrected branch only where raw dark/exposure evidence exists and the field-specific strict-positive validity mask is admitted. Do **not** infer calibrated composition from the present processed TIFF values.

**G0-C — solid MIL:** Reproduce source-faithful temporal MIL using the correct series, its original filtering and **experiment-specific empirical parameters**. Unlike 2020 cases, an accepted 2014-03-07 MIL parameter set is **not yet recovered from a dedicated notebook PDF**, so do not transplant 2020 overrides by default. Sample initial/intermediate/late frames, maintain temporal identity and spatial boundary stability, and compare mask outputs with independent annotated masks. Historical 418 masks can be secondary references once registered, but are not human labels.

**G0-D — liquid-only plume segmentation:** Restrict K-medoids to physically verified liquid pixels, allowing bulk liquid and convective plume subregions, while separately reserving solid/dendrite and invalid chamber pixels. Compare `K={9,12,16,24,32}` with no prefilter, median, Gaussian, nonlocal means and bilateral filtering, using the original v25 method as reference. Also run an unmasked high-K **negative control**, clearly isolating classes captured by solids/background. Compare spatial/temporal plume consistency, manual reference-mask precision/recall and boundary distances on common registered domains—not just K occupancy or reduced optical-intensity RMSE.

**G0-E — chemical calibration:** Use externally supported candidate anchor roles: (i) pre-solidification initial-melt **25 wt.% In, P=0**; (ii) indium-rich solid/dendrite approximately **98.6 wt.%** conditional on verified X-ray-thickness-spanning geometry; (iii) Ga-rich liquid channel **5–10 wt.%** conditional on independent reference. These are the recovered **method's general assumptions**, not independently measured 2014-03-07 chemical anchors. Determine case-specific `P`, reference material and uncertainties, and fit `C_{In}(P)` only for valid material phases; do not treat medoid rank as concentration and do not apply a liquid-only law to solid automatically. Reserve temporally separated blocks/annotated regions as held-out evaluation to avoid pixel-neighbor leakage. Assess fit residuals (wt.%), uncertainty bands and physically implausible extrapolation against the raw measured optical signal.

**G0-F — closure:** Only after the above, register the same-experiment OFV PKL/vector archive, pair-center timestamps, physical pixel pitch, wall boundaries and actual geometric transform. Conservation-law and Hele–Shaw energy tests are later G3/G4 gates, not a substitute for G0 image calibration.

## 3. Evidence acceptance ladder

| Evidence class | Present state |
|---|---|
| A — Static method and calibration-case config | PASS |
| B — Synthetic source-admission/geometry refusal tests | Proposed in this branch; require passing CI |
| C — Exact-source 500 TIFF + 418 mask metadata and SHA import | PASS (X: private artifact with per-input hashes) |
| D — Statistical/temporal MIL and class sensitivity on 2014 frames | Not run on this experimental sequence under the correct 2014 source pipeline |
| E — Paired registered mask pixels + independently annotated ground truth | BLOCKED: geometry and frame mapping |
| F — Native end-to-end calibration with real 2014 radiometry | BLOCKED: reference and chemical anchors |
| G — Independent physical concentration verification | BLOCKED |

**The new test case is accepted as an inventory-backed development fixture, NOT as a quantitative composition-calibration benchmark pass.** Issues [#11](https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis/issues/11) and [#12](https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis/issues/12) track the source/clock and case-specific mask geometry blockers. This report is an append-only extension to the baseline [Phase-0 audit](phase0-nov10-2026-direct-upload-audit.md).
