# T1 Phase 0: dense channel-path and spatiotemporal ablation gate

**Date:** 2026-11-15. **Evidence status:** original source CRC checked; algorithmic hypotheses and *expert-visual* acceptance of selected older morphology masks only. No independently certified physical liquid channels, plume tracks, solid fraction, concentration or source-matched OFV. Original private radiographs and visually accepted masks unchanged.

**Source:** 2014-04-04 original archive SHA256 77fac9a38a9cdaa41ee5ec9c9562acb7149ee1cee8f0246a80c2b267928f2510, 426x761 source pixels. Every replayed source TIFF checks original archive member identity and CRC. Archived detector Reference frames are flat fields; specimen candidate J0 is the median of first 80 main frames. Candidate signed intensity contrast is -ln(I/J0), with valid-pixel Gaussian sigma1; positive >0.02 / >0.04, negative < -0.04, 4-connected area >=25 within provisional detector ROI. Phase and liquid topology remain unknown.

## 1. Explicit channel-to-upper-ROI hypothesis

New experimental source: Python_code/phase0_t1_tentative_liquid_corridor.py. Ten/ten native synthetic tests PASS: unblocked and blocked wall/channel, narrow-neck sensitivity, invalid pixels, unknown front, original-array immutability and geometry refusal.

Given valid original detector pixels V, tentative ROI R and positive log-contrast mask Bplus(tau), define a **traversable hypothesis**, not a physical liquid mask:

    T_tau = V intersect R intersect not(Bplus(tau))

Optionally binary-open T_tau with disk radius r=0, 1 or 2 source px to test whether extremely narrow 2D paths are unreliable. Use a provisional upper-bulk seed in the first 12 ROI rows, restricted to at least 3 pixels above the estimated source morphological front. Flood-fill 4-connected candidate traversable pixels from the seed. For every **pre-existing** negative connected component C, report overlap with the flood-connected candidate area *below* the estimated front. At least 10 overlapping source pixels gives candidate path support. This path proxy is **not** proven liquid metal or channel-to-bulk-fluid in 3D, and does not replace the previously reviewed whole-component morphology gate.

Original frozen morphology: front from expanded positive mask >0.02 by disk closing radius8, bottom-connected support, topmost-per-column curve, median15 and Gaussian2 smoothing, below-front zone with 8-pixel upward margin. The original negative component is retained if >=10 source pixels intersect this zone; owner visually endorsed the front and excluded magenta regions in the reviewed frames.

### Exact-source six-case preview

The source readback independently matched the original negative-mask and morphology kept-mask arrays **pixel-by-pixel** for main1200, main3147 and end297. With r=0 channel opening:

| Source | Morphology retained component count | Candidate paths with strong positive 0.04 as obstacle | Candidate paths with broad positive 0.02 as obstacle |
|---|---:|---:|---:|
| main1200 | 6 | 6 | **0** |
| main3147 | 18 | 13 | 13 |
| end297 | 10 | 6 | 5 |

The earlier/null frames main119 and main480 have no negative components and no front under the original criterion; main639 has a supported front but no negative components. Do not infer from these facts whether the specimen is physically all-liquid.

Private six-case parameter summary SHA256: dec895b73ea52844802238f3697a6ba46a1bd96a77b278082767f9e38aec8d5d.

Three source-coordinate strong-vs-broad obstacle comparison sheets were generated. Green indicates the old provisional front, yellow candidate below-front path, cyan morphology-kept with candidate path, orange morphology-kept without candidate path, magenta morphology-rejected. None is phase ground truth. Full composite source review PNG SHA256: b18cbfb10111948da807f12eb6411f00b9a6bc1adf63f95d1f71e2578a0f6866; private visualization provenance SHA256 6e43ace3e9ee91a082378da2c5c1bc0d616954c048e29def4eccefc3f1b9a100. Raw original TIFFs and source-image PNGs are excluded from public GitHub.

### Full dense original source and frozen graph crosscheck

All **858 original-source frames**, **9,397 candidate negative component nodes** and **20,738 hypothesized temporal associations** in the four approved contiguous windows were checked. Each node ID and morphology-retention decision agrees with the frozen source-checked v0.1 graph; no source gaps or separate end stream are bridged.

| Window | Existing morphology retained | Strong .04 obstacle r0 | Strong .04 obstacle r1 | Broad .02 obstacle r0 | Broad .02 obstacle r1 |
|---|---:|---:|---:|---:|---:|
| main450–700 | 44 | 44 | 44 | 44 | 44 |
| main1120–1280 | 680 | 680 | 678 | 166 | 69 |
| main3000–3147 | 2771 | 2141 | 2141 | 1991 | 1881 |
| end0–297 | 3606 | 2697 | 2609 | 2374 | 2355 |
| **Total** | **7101** | **5562** | **5472** | **4575** | **4349** |

The provisional front is unavailable in **63 earliest frames** of main450–700; no fabricated path is counted for those frames. The contrast between strong and broad barriers is particularly acute in main1120–1280 (678/680 versus 69/680 with a one-pixel opening). Weak positive optical contrast is therefore **not safe to treat unconditionally as a solid barrier**. These values are optical 2D connectivity hypotheses and must not be interpreted as plume recall or actual confirmed bulk-connected channels.

Full dense path crosscheck private summary SHA256: **4ff18f9a1b9e8f78989f79e523f36f3295ca5e1d04d74322154151ea98bda708**.

## 2. Four-way T1 ablation on frozen source-verified graph

**Methods:** Raw = all candidate negative components; spatial = owner-reviewed morphology gate; temporal = any adjacent-frame association in T1 v0.1; strict spatial AND temporal = *diagnostic test only*. Combined-safe mode retains unchanged morphology masks and merely annotates path and temporal support. Edge existence is NOT independently verified actual plume motion.

| Candidate decision | Component nodes | Pixel-frame occurrences across 858 frames |
|---|---:|---:|
| Raw negative threshold | 9,397 | 3,488,632 |
| Spatial morphology only | 7,101 | 3,318,534 |
| Temporal-link only | 9,176 | 3,441,941 |
| Strict spatial AND temporal (not production) | 6,926 | 3,273,480 |

**Negative finding 1:** temporal-only would include 2,250 spatially rejected nodes (168,461 candidate pixel-frame occurrences); some may correspond to already expert-rejected upper artifacts. Persistence is insufficient.

**Negative finding 2:** strict intersection would delete 175 morphology-kept but temporally unlinked nodes (45,054 pixel-frame occurrences); genuine plume births or short-lived structures may be among them. The three reviewed anchors main1200, main3147, end297 happen to keep all accepted pixels under strict intersection, but this small sample does NOT justify a global rule.

**Reproducibility:** ablation JSON SHA256 **b97a59c835061b45c97966bdf96be2c29cdb882289a4286ec7fee4aaf09770e4**, independently regenerated byte-for-byte from original immutable graph SHA-checked JSONs. These counts are source-pixel-frame candidate statistics, not physical area, true segmentation precision/recall or optical-flow trajectory accuracy.

## 3. Interpretation and next expert gate

- Keep existing morphology-only classification frozen for review and provisional analysis.
- Report source-linked T1 temporal associations and candidate 2D path support as **separate interpretability features**, not new hard segment deletion.
- Existing ten high-centroid-score/low-native-mask-shape-IoU adjacent pairs are in the private X: source-coordinate reviewer archive, two full-resolution contact sheets and two 4x zoom sheets. The experiment owner should classify each as supported physical lineage, incorrect link or uncertain; do not infer a label from IoU alone.
- Separately review the source-coordinate strong-versus-broad channel contour comparisons, particularly main1200 and the channel-like lower image region main3147.
- Only after *independently annotated original-frame* physical liquid/solid boundaries, actual bulk-liquid seed and source-registered motion can the spatial+temporal+channel model be calibrated or compared by true accuracy. Retain stationary detector defect and transient moving/split/merge plume controls.

Scientific PR #22 remains DRAFT stacked on PR #20. The Zensical site PR #21 was merged and deployed independently; no private experimental images or institutional artwork were added to that public site.
