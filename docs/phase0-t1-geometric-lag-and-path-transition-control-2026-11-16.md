# T1: source-hashed geometric temporal-lag and tentative channel-state challenge

**Date:** 2026-11-16. **Status:** exploratory diagnostic, not physical plume ground truth, a false-positive rate or a source-to-liquid-channel proof. The original source radiographs, previously owner-reviewed candidate morphology masks and production segmentation remain unchanged.

## Source provenance

Original 2014-04-04 radiograph archive SHA256: **77fac9a38a9cdaa41ee5ec9c9562acb7149ee1cee8f0246a80c2b267928f2510**. Frozen T1 v0.1 graph files were previously built by verifying original TIFF archive member identity/CRC. This study reads and hashes only those frozen component graph files and the separately frozen per-component tentative-channel path states. It does not reread, reclassify or publicly distribute original image pixels.

Four approved contiguous source windows: main450–700, main1120–1280, main3000–3147, end0–297; collectively 858 source frames, 9397 negative candidate components and **20738 T1 v0.1 candidate association edges**. Original source-acquisition groups remain separated.

- Prior private exact source-frozen analysis SHA256 **585c94da85a947c62447586041035a90873edd3656e66d5d3f4c3c95ff7ce3da**.
- New independent pure-Python analysis module: Python_code/phase0_t1_geometric_lag_and_path_controls.py; 11/11 native synthetic tests PASS in tests/test_phase0_t1_geometric_lag_and_path_controls.py.
- Private full independent new-code replay SHA256 **af4e561c7db233ec1226c430d617b5464f5a03e385176ad2aabe69df3bf65b45**, reproducing **exactly** every previous window-by-lag admitted-pair count, high-score count, component opportunity count and tentative-channel label-switch count.

## A. Geometric coincidence versus original-frame lag

The v0.1 T1 gated (unnormalized) geometric score for compatible component centroids, area and elongation is

$$
s_{ij}=\exp\left[-\frac12\left(\frac{\lVert\mathbf c_j-\mathbf c_i\rVert}{30\alpha}\right)^2\right]
\left(\frac{\min(A_i,A_j)}{\max(A_i,A_j)}\right)^{1/2}
\left(\frac{\min(\epsilon_i,\epsilon_j)}{\max(\epsilon_i,\epsilon_j)}\right)^{1/4},
\qquad
\alpha=\min\!\left(1.5,\max\left(0.3,\frac{\Delta t}{1000\,\mathrm{ms}}\right)\right).
$$

Other hard gates: centroid distance no more than 30 alpha pixels, maximum area ratio 8, same acquisition group. For **true original source-adjacent frames**, use the frozen candidate time increment **1000 or 1001 ms**, accounting for cumulative original time rounding. Thus the model reproduces all **20738** original candidate edges.

For **nonadjacent** source frames separated by 3, 5, 10, or 25 original-frame ordinals, calculate the *same* geometric gate with a **virtual 1000ms pair interval**, without making any accepted T1 link. This tests geometric coincidence propensity at longer temporal separation, not physical trajectory truth. Stationary camera defects **and real persistent plume structures** can remain geometrically similar for many frames; these pairs are NOT guaranteed physical negative matches.

Normalize admitted pairs by the number of component-pair opportunities for each lag; raw counts are misleading because farther lags have shorter comparable source windows.

| Source window | Lag 1 | Lag 3 | Lag 5 | Lag 10 | Lag 25 |
|---|---:|---:|---:|---:|---:|
| main450–700, very sparse | 80.00% | 66.67% | 73.68% | 73.91% | 92.86% |
| main1120–1280 | **40.08%** | 40.02% | 40.10% | 39.85% | **39.44%** |
| main3000–3147 | **6.83%** | 6.84% | 6.75% | 6.74% | **6.59%** |
| end0–297 | **17.58%** | 17.61% | 17.61% | 17.46% | **17.23%** |

Unnormalized admitted component-pair totals across all four windows: lag1 **20738**, lag3 **20554**, lag5 **20187**, lag10 **19608**, lag25 **17733**. They must **never** be interpreted as physical true- or false-link counts.

**Finding:** the v0.1 geometric gates alone offer little temporal-separation discrimination in the populated windows. Centroid proximity/area/elongation may be necessary preliminary gates but cannot establish actual moving-plume lineage, and their unnormalized scores are not probabilities.

## B. Source-graph tentative-channel path-label transitions

Separately, the existing pilot of a 2D original-detector path flood-fill considers pixels that are *not positive-contrast detections*. It compares positive obstruction thresholds +0.04 (strong) and +0.02 (broad), with optional one-pixel opening. These are **candidate unblocked optical paths**, not physical 3D Ga-rich liquid, solid-phase ground truth, or actual plume origin. For every immutable original T1 candidate temporal edge, count when its endpoints have different candidate path-supported labels. A change may arise from segmentation noise, physical evolution, source-morphology sensitivity or a wrong association; it is not automatically an actual channel breakup.

| Source window | Strong +0.04 barrier with 1px opening: path-label switches | Broad +0.02 barrier with 1px opening |
|---|---:|---:|
| main450–700 | 0/24 (0%) | 0/24 (0%) |
| main1120–1280 | **4/1180 (0.34%)** | **158/1180 (13.39%)** |
| main3000–3147 | 36/11612 (0.31%) | 585/11612 (5.04%) |
| end0–297 | 476/7922 (6.01%) | 557/7922 (7.03%) |

When both endpoints are already morphology-retained, main3000–3147 has **0/5612** path-label changes with the strong barrier versus **549/5612 (9.78%)** with the broad barrier. For end0–297: **228/7647 (2.98%)** versus **309/7647 (4.04%)**.

**Finding:** promoting weak-positive optical contrast to definite solid obstruction can create strong instability of hypothetical source-to-upper-ROI path support, especially in developing main1120–1280. These results support keeping weak positive structure as uncertain, NOT declaring the +0.04 solid-barrier model physically correct.

## C. Three-original-frame candidate triplet kinematics (source-hashed replay)

New public code: Python_code/phase0_t1_triplet_motion_diagnostic.py and tests/test_phase0_t1_triplet_motion_diagnostic.py. Eleven native synthetic tests PASS, explicitly including straight constant-velocity motion, a genuine 90-degree turn, a stationary detector defect with perfect zero-acceleration, split/merge multi-path candidates, source 1001ms timing, group/time gap rejection and original-data nonmutation. This diagnostic consumes and checks *the already-frozen original T1 component graphs*, not original radiograph pixels or source-unregistered OFV.

For every two-edge candidate graph path A->B->C in three strictly adjacent source ordinals and the **same original acquisition group**, let the original-detector centroid velocity estimates be

$$
\mathbf v_1=\frac{\mathbf c_B-\mathbf c_A}{t_B-t_A},
\qquad
\mathbf v_2=\frac{\mathbf c_C-\mathbf c_B}{t_C-t_B}.
$$

The diagnostic velocity jump and turning angle are

$$
\Delta_v=\lVert\mathbf v_2-\mathbf v_1\rVert,
\qquad
\vartheta=\arccos\frac{\mathbf v_1\cdot\mathbf v_2}{\lVert\mathbf v_1\rVert\,\lVert\mathbf v_2\rVert}.
$$

The angle is **undefined** unless both centroid speeds reach the declared sensitivity threshold of 1 source pixel/s. Separately flag both speeds below 0.5px/s as *near stationary*, and angles at least 120 degrees as *large direction changes* **for review only**. These are **not scientifically optimized cutoffs**, not true fluid acceleration measurements and not universal plume rejection criteria.

| Frozen original-source window | Two-edge candidate paths | Middle nodes with multiple candidate predecessors/successors (paths) | Near-stationary candidate paths | Angles at least 120 degrees / paths where orientation is defined |
|---|---:|---:|---:|---:|
| main450–700 | 13 | 10 | 0 | 9 / 10 |
| main1120–1280 | 2,438 | 2,263 | 59 | 962 / 1,674 |
| main3000–3147 | **33,753** | **32,703** | 810 | **14,183 / 27,282** |
| end0–297 | **21,318** | **20,399** | 1,384 | **7,459 / 11,617** |
| **Total** | **57,522** | **55,375** | **2,253** | **22,613 / 40,583** |

Full original-source-graph SHA256-checked triplet diagnostics report SHA256: **0cc14d49971f3db9031022d4aab4b086d0caa4226f72a89a9f9f9486273f8437**.

**Interpretation:** the candidate graph permits many simultaneously competing A->B->C paths, particularly in the later high-component-density sequence. Large apparent centroid direction changes can reflect wrong geometric associations, real plume turns, deformation, or split/merge events. A perfectly stationary detector artifact will have zero velocity jump and can satisfy a simple smooth-motion penalty better than a genuine moving plume. Therefore **triplet acceleration minimization cannot by itself disambiguate physically correct lineage**.

This is a pre-selection **diagnostic**, not a production graph fitter. A defensible next test must simultaneously evaluate motion/shape/contrast, explicit source-coordinate artifacts, genuine birth/split/merge and independently classified expert temporal links. No existing T1 edge or morphology decision is changed.

## D. Next falsification and owner review

1. Retain the frozen morphology-only segmentation. Temporal links and candidate channel status remain separate, interpretable evidence annotations, not new hard keep/reject rules.
2. Await independent expert classification of the existing ten temporal pairs (correct lineage / incorrect association / uncertain), original-frame phase boundaries and source-to-bulk-liquid channels. A source-linked private ZIP with the editable 19-row review ledger is already prepared for owner review.
3. Trial a **triplet motion-and-shape-consistency diagnostic** on three adjacent original source frames, testing genuinely moving/deforming, merging/splitting and detector-stationary synthetic controls. Do not bring in unregistered OFV flow before the independent G0 source-time/crop calibration gate.
4. Do not report precision/recall or a physical track count until independent held-out annotations are available; hold out complete source-time segments, not individual randomly selected nodes of the same tracks.
5. Keep both positive-obstacle thresholds as sensitivity branches and explicitly represent optical interfacial uncertainty. Do not train T2 CRF probabilities from automatically generated T1 labels.

**Repository gate:** documentation PR #23 was explicitly approved, merged and deployed to public Pages; scientific PR #22 remains DRAFT stacked on unmerged PR #20. None of these exploratory findings authorize merging scientific PRs or publishing private source images.
