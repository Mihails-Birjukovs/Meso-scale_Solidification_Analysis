# T1 v0.2 — graded motion, shape, tentative-channel evidence and weight sensitivity

**Scientific status:** exploratory review ranking, not validated physical plume-lineage identity. **Date:** 2026-11-16. **Code:** Python_code/phase0_t1_graded_lineage_evidence.py and Python_code/phase0_t1_weight_grid_sensitivity.py. **Original source archive:** 2014-04-04, SHA256 **77fac9a38a9cdaa41ee5ec9c9562acb7149ee1cee8f0246a80c2b267928f2510**.

The original source TIFFs, previously accepted morphology-only masks, review decisions, candidate graph edges and original v25 Mathematica notebook were unchanged. Experimental code remains in draft PR #22, stacked on unmerged draft PR #20.

## Fixed source authority and evidence conditions

All 858 approved original source frames were reimported with original archive member CRC/inventory validation. Each of the original 9,397 source-detector negative components was checked against its frozen candidate component ID, area, original centroid, morphological zone overlap and owner-reviewed baseline status. Every one of 20,738 original candidate adjacent-frame edges was reconstructed from source components with **identical edge identity and recorded 1,000/1,001ms candidate source interval**. Original mask acceptance is a separate, *unchanged* field; no experimental score can promote an expert-rejected magenta component.

The model produces five *diagnostic* cues for a candidate link \(i\to j\):

- \(G_{ij}\): original T1 geometric compatibility score, unnormalized and not a probability.
- \(H_{ij}\): original detector-pixel binary mask IoU after *observed-centroid* alignment. It uses both observations; it is optimistic, not an independently predicted flow field.
- \(M_{ij}\): triplet motion consistency, calculated from the median competing A→B→C original source-adjacent centroid-velocity jump ratio. With no 3-frame continuation this cue is **missing**, not zero.
- \(L_{ij}\): hypothetical 2D upper-liquid-like *not-positive optical path* support under two positive-obstacle thresholds. Both endpoints supported by broad and strong masks gives 1; supported by strong-only gives 0.5; otherwise **unknown**. It cannot certify physical 3D Ga-rich liquid connectivity.
- \(U_{ij}\): the inverse square-root candidate graph branching degree, a useful competitor-count penalty but **not independent physical evidence**.

The predeclared motion and candidate-degree diagnostics are:

$$
M_{ij}=\frac{1}{1+\operatorname{median}_{p\ni(i,j)} R_p},
\qquad
U_{ij}=\frac{1}{\sqrt{d_i^+d_j^-}}.
\label{eq:t1-v02-motion-degree}
$$

The five weights were **predeclared before the new complete source replay** and were never fitted:

$$
\begin{aligned}
(w_G,w_H,w_M,w_L,w_U)&=(0.10,0.30,0.30,0.15,0.15),\\
S_{\mathrm{low}}&=\sum_{k:E_k\ \mathrm{known}}w_kE_k,\\
S_{\mathrm{high}}&=S_{\mathrm{low}}+\sum_{k:E_k\ \mathrm{unknown}}w_k.
\end{aligned}
\label{eq:t1-v02-uncalibrated-interval}
$$

The interval is **not a statistical confidence interval** and the score is **not a calibrated posterior probability**. Missing evidence expands the admissible heuristic score range rather than being silently set to a negative physical observation. Predeclared priority-only classes: high-corroboration if both endpoints are already morphology retained, all cues available, lower score at least 0.75, and no candidate-degree ambiguity or near-stationary triplet counterexample; otherwise abstain or preserve the original morphology rejection. Neither an edge nor a pixel is deleted by scoring.

## Fixed source-time-separated evaluation

These blocks were fixed before the v0.2 complete replay, but **not genuinely prospective/blinded holdouts**: some frames had been inspected previously. The split separates reporting and rule application, not physical truth labels.

| Original source block | Role | Frames | Candidate nodes | Morphology-retained nodes | Frozen T1 edges | Full five-cue edges |
|---|---|---:|---:|---:|---:|---:|
| main450–700 | Sparse control | 251 | 44 | 44 | 24 | 15 |
| main1120–1280 | Development reference | 161 | 680 | 680 | 1,180 | 1,168 |
| main3000–3147 | Late fixed-rule evaluation | 148 | 5,021 | 2,771 | 11,612 | 4,995 |
| end0–297 | Separate-stream fixed-rule evaluation | 298 | 3,652 | 3,606 | 7,922 | 5,497 |
| **Total** | — | **858** | **9,397** | **7,101** | **20,738** | **11,675** |

Across all candidate edges: 14,463 had two previously morphology-retained endpoints; 18,617 had competing degree-ambiguity; 9,016 lacked the path-corroboration cue; 91 lacked three-frame motion. Every original detector-pixel shape was reprocessed, with **no missing shape** in this replay. Nothing here is a validated true-/false-plume-link count or a segmentation precision/recall metric.

**Private source-CRC-verified full original replay SHA256:** **229a1f6b1f7e5f023e8baf858ce5640e0e4a79e6d1059182764ba65bb834e1a0**.

## Independent full score readback

A **second** frozen-record audit recomputed all 20,738 edge features with the public scoring routine and confirmed exact source edge identities, original T1 geometric scores, shape IoU, median candidate motion, hypothetical root flags, score endpoints, source-morphology decisions and review tiers. No original frames were rewritten. **Independent readback SHA256:** **a94c80da1fdd5b317eeac846d78f7efee002aed29163e8f1aef21ae49bf7dfa6**.

This tests numeric and source-to-graph reproducibility, not independently adjudicated physical plume identity.

## 11 predeclared weight scenarios — a negative result

A separate public pure-Python sensitivity module tested (a) original reference weights, (b) omission of each of the five cues with other weights normalized, (c) uniform weights, and (d) increased emphasis on shape, motion, tentative channel or graph uniqueness. The weight grid was fixed before source outcomes were examined; no training or optimization occurred. This step is a reviewer-priority sensitivity analysis, **not scientific accuracy**.

| Original source block | Baseline high-corroboration links | Still high across **all 11** weight scenarios |
|---|---:|---:|
| main450–700 | 0 | 0 |
| main1120–1280 | 12 | 2 |
| main3000–3147 | 215 | 82 |
| end0–297 | 306 | 132 |
| **Total** | **533** | **216** |

Only **216/533 = 40.5%** of the original high-corroboration *review-priority candidates* remained high under all eleven alternatives. This confirms that an arbitrary single weighted threshold is fragile and must **not** be promoted into a hard temporal mask/track selector.

**Complete private sensitivity summary SHA256:** **b6733b12620a21df85c4d44813eb3740871092ec1683d152144745ab1ddeeff6**.

## Acceptance ledger

- PASS: all original 858 source frames imported with CRC; source-derived connected components, frozen morphology gate and 20,738 candidate graph edges reproduced.
- PASS: nonphysical heuristic intervals/tiers computed and independently rerun exactly, all source/record hashes preserved.
- PASS: 14 new native graded-model synthetic tests and 9 new native weight-grid tests, including absent-path non-evidence, stationarity, branch ambiguity and no source mask promotion.
- PASS (conditional on workflow run): dedicated pinned-dependency synthetic CI must be checked separately; no single CI green status can validate true plume trajectories.
- BLOCKED: independent expert source-coordinate *same-plume* labels, phase and channel masks, real split/merge/birth/death ground truth, reliable source-registered physical OFV, temperature/boundary history and G0 absolute concentration.
- NOT DONE: automatic rank-to-physical-ID assignment, T2 probability calibration, physically accepted masks/tracks or true association precision/recall.

The previous **19-row owner review ledger and source-linked review contact sheets** stay intact on authorized X:. They are not overwritten by v0.2 candidate ranks. A truly prospective blockwise holdout and independent expert labels are prerequisites to fitting weights, selecting thresholds, making physical track claims or merging the science PR.

**Data rights:** private original TIFFs, per-edge detector-pixel features and review contact sheets remain private on authorized X:. Only source-generic algorithms, independent tests, source SHA summaries and scientific caveats appear in this public draft.
