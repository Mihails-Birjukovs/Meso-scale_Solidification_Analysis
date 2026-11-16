# T1 link-specificity gate: original source shape diagnostics

Date: 2026-11-15. **Scientific status: exploratory component-association diagnostics, not physical plume tracking or phase ground truth.**

## Frozen dense-window graph topology

The T1 v0.1 source-CRC-verified replay comprised 858 frames, 9,397 negative candidate component nodes and 20,738 possible temporal association edges. A second read-only study of frozen graph JSON found 6,608 nodes with multiple candidate parents or children (70.3% overall). A multiple-edge node is **not automatically a false association**: actual channels/plumes may split and merge.

| Window | Nodes | Edges | Multi-neighbor nodes |
|---|---:|---:|---:|
| main450–700 | 44 | 24 | 8 |
| main1120–1280 | 680 | 1180 | 430 |
| main3000–3147 | 5021 | 11612 | 3649 |
| end0–297 | 3652 | 7922 | 2521 |
| **Total** | **9397** | **20738** | **6608** |

Private frozen-graph metrics SHA256: ee705a65e6333a040585f4e8fac722871f20e22c97d23f70b803dccf2d1e3925.

## Source-pixel shape link evidence

The additive experimental module Python_code/phase0_t1_pixel_shape_link_diagnostic.py compares each *existing* T1 edge using:

1. Original detector-pixel component intersection-over-union (IoU) with no registration.
2. A rigid translation of the earlier footprint by the **observed** centroid shift, followed by IoU. This is an optimistic shape check because it uses the later observation; it is **not a causal independent motion predictor**.
3. The native source shift and fraction of pixels clipped by the detector boundary.

No original edge is deleted and no component spatially rejected by the reviewed morphology gate is restored to an accepted plume. Eight native synthetic tests passed, including rigid translation, mismatched shape near identical centroids, unchanged edge counts, valid source geometry and a stationary detector artifact with perfect IoU.

## Real source diagnostic replay

The diagnostic was replayed on 1,673 candidate edges using CRC-checked original source TIFF frames from the 2014-04-04 archive (archive SHA256 77fac9a38a9cdaa41ee5ec9c9562acb7149ee1cee8f0246a80c2b267928f2510):

| Review window | Edges | Optimistic aligned IoU median | IoU at least 0.4 |
|---|---:|---:|---:|
| main1196–1204 | 42 | 0.2821 | 16 |
| main3143–3147 | 304 | 0.3282 | 109 |
| end293–297 | 91 | 0.3667 | 43 |
| main1120–1140 | 84 | 0.2543 | 34 |
| main3000–3020 | 1152 | 0.3095 | 403 |
| **Total** | **1673** | No pooled median reported | **605** |

Original-pixel diagnostic manifest SHA256: 0a034028f2e5591b28b798c9b262634bebb387ac9d8ba450db31486cf336647a.

Ten high-score but weak shape-IoU associations were selected for experiment-owner visual review. Two native full-frame pairwise comparison contact sheets and two matched-native-coordinate 120x120px crops at 4x nearest magnification were created and kept **private**, not uploaded to public GitHub. The original-coordinate selected components are cyan, native bounding boxes magenta, centroids yellow and provisional front green. The corresponding private full-frame reviewer manifest SHA256 is 9be1ecd250e074271e8f5bb15e8938cc9ef8297784e8e3d4434a63a17a0e2900; zoom reviewer manifest SHA256 ddfc3810c912fd48e768001c03474c7fe4d33eb736057ce077e1d8e492e141bc.

## Interpretation and next test

Aligned pixel IoU as low as 0.25–0.37 across these windows shows potential graph ambiguity, not confirmed physical false links. Genuine deforming, split and merging plumes can have low IoU; persistent sensor artifacts can have high IoU. Therefore **do not impose a global IoU cutoff yet**. First review the ten flagged associations and synthetic counterexamples; compare shape-gated and non-shape-gated graph ablations on held-out, independently annotated time blocks.

Retain original reviewed morphology outputs and main1200/main3147/end297 exact mask comparisons. T1 graph edges remain candidate hypotheses. Sample temperature history, physical chamber/phase geometry, true liquid-channel-to-bulk connectivity and source-registered OFV are separately unverified G0 gates.

No publication of private TIFFs/review contact sheets, no production-mask promotion and no PR merge is implied.
