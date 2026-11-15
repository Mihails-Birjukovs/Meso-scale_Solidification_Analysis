# Phase 0 — owner-reviewed 2014-04-04 candidate masks: focused sensitivity and uncertainty gate

**Date:** 2026-11-15. **Scope:** original 2014-04-04 Ga–In radiography, original archive SHA-256 `77fac9a38a9cdaa41ee5ec9c9562acb7149ee1cee8f0246a80c2b267928f2510`. This is a **non-destructive exploratory follow-up** to draft PR #20's 21-frame candidate-mask benchmark. The original raw TIFFs, owner-approved reference masks, numerical CSVs, original v25 Mathematica notebook, and optical-flow production logic remain unchanged.

## 1. Owner qualitative review — preserve the original judgment

The experiment owner reviewed the six-frame red/cyan overlay package, marking two areas on screenshot examples for original main frame 3147.

| Original source | Owner observation | Accepted scientific status |
|---|---|---|
| main 119 | Good; agrees | Visual agreement with current candidate overlays; **not independently segmented phase ground truth** |
| main 480 | Approved | Visual agreement with early candidate overlays; not proof of all-liquid/cooling state |
| main 639 | Ambiguous newly solidifying regions | Candidate positive mask should be evaluated under more inclusive thresholds; do not force intermediate liquid/solid pixel assignments |
| main 1200 | Negative mask makes sense; positive mask contains intermediate regions | Keep original negative reference for comparison; uncertain positive transition should be explicitly tracked |
| main 3147 | Negative mask mostly good except marked upper isolated patches; positive generally plausible except green-marked intermediate/mushy-looking material | Upper scattered negative candidates disputed; positive-to-liquid transition **not binary human truth** |
| end 297 | Looks good | Current candidate overlays visually plausible; avoid retroactive global threshold change without comparing to this case |

The two uploaded screenshots are preserved in the conversation, not silently interpreted as source-coordinate polygon ground truth. Their manually drawn purple/green rectangles are **not registered to native 761×426 source pixels**. This review is independently recorded at `docs/phase0_calibration_cases/2014-04-04-owner-qualitative-candidate-mask-review-2026-11-15.json` and privately on X:.

## 2. What was actually run

Run source `Python_code/phase0_2014_04_04_targeted_mask_sensitivity.py` on the authorized Windows workstation using **existing compatible Miniconda Python, NumPy 1.26.4/SciPy 1.13.1**. The script imports previously vetted original benchmark code and SHA/CRC-checks the source manifest, all **111 Reference flat-field TIFFs**, first **80 main experiment TIFFs** making provisional `J0_candidate`, and all six reviewed original source TIFFs (main 119/480/639/1200/3147; end 297). It independently re-creates all **18 original Gaussian-1px, |log contrast|=0.04, 25-pixel connected-component masks** and refuses any pixelwise discrepancy. The output was created in a **new, versioned X: directory**; the authoritative original review files were only read.

The original `Reference` acquisition is a **detector flat field**, not initial homogeneous Ga–25 wt.% In specimen baseline. Experimental `P_candidate=-ln(I/J0_candidate)` in this flat-only branch is provisional; it is not accepted physical optical density or chemical indium concentration. The displayed source ROI y=[120,412), x=[155,690) is **unapproved candidate detector geometry**; independent chamber and solid/liquid masks still do not exist.

- Positive mask sweep: Gaussian σ=1px, Gaussian σ=2px, and median 3×3 filters; log thresholds **0.02, 0.025, 0.03, 0.035, 0.04, 0.05, 0.06, 0.08**, minimum 25-pixel 4-connected components: **6×3×8=144** source/filter/threshold evaluations.
- Negative mask sweep: same three filters, negative thresholds **0.04, 0.05, 0.06, 0.08**, minimum component sizes **25, 75, 150 pixels**, **6×3×4×3=216** evaluations.
- Two unapproved spatial diagnostic windows only: **upper strip** y=[120,175),x=[155,690), and **central channel** y=[175,412),x=[335,485). These are *not* mathematically registered to the user's green/purple screenshot rectangles, and they are not trusted sample or phase regions.
- Review images use the same fixed `[-0.12,+0.12]` color range with original 761×426 source pixels, red = positive candidate outline, cyan = negative candidate outline, amber = **newly added low-confidence positive candidate** (threshold 0.02 **minus** baseline 0.04), plus black outline halos.

## 3. Positive threshold observations

At Gaussian σ=1px, min component=25, the counts of **image-change candidate pixels** inside the unapproved source rectangle are:

| Source | t=0.02 | t=0.03 | Current t=0.04 | t=0.08 |
|---|---:|---:|---:|---:|
| main 119 | 0 | 0 | 0 | 0 |
| main 480 | 321 | 194 | 70 | 0 |
| main 639 | 6,090 | 4,128 | 2,146 | 90 |
| main 1200 | 39,918 | 35,005 | 28,785 | 3,701 |
| main 3147 | 106,104 | 91,946 | 75,259 | 22,782 |
| end 297 | 128,047 | 121,245 | 111,269 | 43,108 |

**Interpretation:** lowering 0.04→0.03 adds +1,982 / +6,220 / +16,687 positive candidate pixels in main 639/1200/3147, respectively (+92%, +22%, +22% relative to the current mask). Lowering to 0.02 adds many more, including weakly contrasted areas which may be mixed solidifying material, liquid artifacts, or background bias. We should **compare t=0.03 as a conservative expanded-candidate hypothesis**, but not promote it to a solid-phase label without independent boundary assessment.

The output uses a **two-tier candidate uncertainty display**, not a scientific phase-fraction model: baseline positive candidates are red, and the additional low-contrast positive pixels admitted by 0.02 but absent at 0.04 are amber. The background `-ln(I/J0_candidate)` remains untouched. This explicitly makes ambiguous/intermediate structures visible for review.

## 4. Negative upper-fragment trade-off

At Gaussian σ=1px, min component=25, **main 3147** negative candidates:

| Threshold | Upper diagnostic strip pixels | Central channel pixels | Full candidate negative pixels |
|---|---:|---:|---:|
| 0.04 (current) | 1,698 | 6,064 | 8,326 |
| 0.05 | 161 | 4,886 | 5,452 |
| 0.06 | 25 | 3,956 | 4,299 |
| 0.08 | 0 | 2,101 | 2,240 |

This supports the owner's concern that the upper scattered negative detections are particularly low contrast. But **main 1200**'s negative channel-like region shrinks **432→190→95→0** pixels under those same successive thresholds; the negative detections in the visually approved **end 297** are also eroded. Increasing area filtering *alone* (t=0.04, min area 25→150) only reduces upper-band candidates in main 3147 from **1,698→1,111**, while central-channel detections drop from 6,064→5,507. A blanket threshold/area change cannot be endorsed for all frames yet.

**Next approach to explore separately:** time-consistent plume geometry or a candidate lower-front-connected negative detection policy with alternative area/noise rules. Avoid forcing front geometry or plume chemistry from unapproved original detector ROIs; source registration and independent expert phase constraints remain required. Do not silently delete the owner-disputed upper pixels from authoritative masks.

## 5. Outputs and scientific validation

Private workspace:

`X:\AI-Lab-Test\Solidification_OFV\analysis_outputs\phase0_2014-04-04_targeted_mask_sensitivity_2026-11-15\sweep_v1`

- `main_0639_positive_threshold_review_v1.png`, `main_1200_positive_threshold_review_v1.png`, `main_3147_positive_threshold_review_v1.png`: seven-column original source-log heatmap plus 0.02/0.03/0.04/0.06/0.08 positive contours and the amber-vs-red-vs-cyan comparison.
- `main_3147_negative_threshold_area_review_v1.png`, `main_1200_negative_threshold_area_review_v1.png`, and `end_0297_negative_threshold_area_review_v1.png`: 2×4 negative threshold/area choices, all using original detector pixels and a constant color scale.
- Additional positive review sheets for main 119/480 and end 297 act as visually accepted reference/control images.
- `focused_positive_parameter_sweep.csv`: 144 numeric rows. SHA256 `09E8D94F1E6BBBB279F16C31EE695F9191452073B8C111A07327561D918837C0`.
- `focused_negative_parameter_sweep.csv`: 216 numeric rows. SHA256 `3C4DB3AA34D971A8C94A19F787E373AFA33BDD357C1CBB5A3FB983A56C9F6C56`.
- `focused_sensitivity_manifest.json`: source hashes, conditions, status restrictions and reviewed frames. SHA256 `F857B08A238F08BF641646EC3D139E3D1476D35169A1747318CF09592405B313`.
- Main 3147 positive 7-column sheet SHA256 `150BA96C01AB6AACC703C58CF4A2C4F0A55FADA43CDA22BA1B8A26AFD348C5BF`; main 3147 negative matrix SHA256 `1181B517DA01F94700AC6D929F270AFFE90FBF2631987217897CD4833D5B2636`.
- Derived five-layer boolean NPY bundles stored for each reviewed frame: broad 0.02, baseline 0.04, strong 0.08, newly added weak 0.02\0.04 and existing negative 0.04. They are new experimental artifacts, **not substitutions for the authoritative original PNG masks**. Separate resized `PREVIEW_*` PNGs were created only for faster visualization and do not supersede the source-native review sheets.

Independent **native workstation** validation: six synthetic test cases in `tests/test_phase0_2014_04_04_targeted_mask_sensitivity.py` PASS under compatible scientific packages (shape, threshold nesting, reproducible overlays, default detector invalid color, weak amber classification and preservation of original array). The **actual source replay** independently checked all 18 earlier masks for pixel-exact equality and checked source TIFF member CRCs. GitHub lightweight CI may skip scientific packages; its green status is not validation of physical phase truth.

## 6. Scientific acceptance policy

1. **Do not relabel red/amber positive intensity anomalies as confirmed solid.** Distinguish optically strongly positive material, weak or mushy-zone-like interface, bulk liquid and invalid detector pixels. Whether a partially solidifying region belongs to solid depends on the operational definition (any visible solid network, majority solid fraction, full path-thickness solid, etc.), which cannot be resolved by RGB overlays alone.
2. A **three-category reviewer outcome** is appropriate at this stage: clear solid-like morphology, uncertain/interfacial mixed appearance, and clear liquid-like morphology. Plume-like negative anomalies are a separate *optical* hypothesis, not a chemical label. Geometry uncertainties should be logged.
3. The current threshold 0.04 remains an unchanged baseline reference. **No new threshold has been accepted** as production or historical v25 behavior.
4. Preserve user notes from screenshots, and obtain native source-coordinate masks/polygons if pixelwise IoU/ground truth will ever be computed.
5. Full v25 time-derived MIL dynamic threshold, source-matched OFV, laboratory temperature chronology and physical chemical calibration remain independently open gates.

**GitHub:** changes to reusable benchmark source, tests, the owner's qualitative review ledger and this report are on draft PR #20, unmerged; no separate Gmail monitoring.
