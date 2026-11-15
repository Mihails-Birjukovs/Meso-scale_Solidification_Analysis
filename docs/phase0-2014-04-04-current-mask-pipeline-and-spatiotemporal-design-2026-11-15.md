# 2014-04-04: Exact current candidate-mask pipeline and proposed spatiotemporal model

**Prepared 2026-11-15.** **Status:** Source-backed documentation of the implemented method, followed by an **unimplemented** model proposal. The original Ga–In source archive is SHA256 **77fac9a38a9cdaa41ee5ec9c9562acb7149ee1cee8f0246a80c2b267928f2510**. All reviewed candidate masks, source TIFFs, original Mathematica v25 notebook and source archive remain unchanged.

**Source files, PR #20 draft:** Python_code/phase0_2014_04_04_mil_candidate_benchmark.py (original log masks); Python_code/phase0_2014_04_04_targeted_mask_sensitivity.py (parameter sweeps and saved input arrays); Python_code/phase0_2014_04_04_morphological_zone_pilot.py (zone/front and component gate). Historical distinct authority: Mathematica_code/Dendrite & Plume Analysis v25.nb, Git blob b13ef6adda22405d89680e3ebe5da50e6f40d297. **The Python procedure is NOT the historical native temporal MIL/dynamic-threshold pipeline.**

## A. The exact method CURRENTLY implemented

### A1. Source and validity

Original source TIFFs are 426 rows x 761 columns, uint16, top-left origin, x right and y down. Experimental streams are main (3,148) and end (298), and separate 111-image Reference recording is the detector **flat field**, owner-confirmed. Original member size and CRC32 are checked using the archive inventory. The explicit candidate ROI is half-open array coordinates **y=[120,412), x=[155,690)**, NOT a physically accepted chamber boundary.

The main stream has three candidate filename-time acquisition gaps before zero-based ordinals 919 (4.360 s), 1836 (4.359 s) and 2770 (3.813 s); end is a separate stream. Filename times are not certified instrument timestamps. These gaps must be explicit breaks in any future temporal graph.

Flat-only working branch; **no additive dark-current correction**. The per-pixel candidate sample baseline J0 is the median of **the first 80 original main experimental TIFFs**, distinct from the detector flat-field recordings. The Reference flat images currently provide detector validity: all 111 must have 0 < R_k < 65535. The sample frame I_t and J0 must likewise each be strictly within (0,65535). Invalid pixels are not measurements, even though the internal P array stores zero at their indices.

On these jointly valid pixels, the code defines signed, *provisional* contrast:

P_t(x,y) = -ln[I_t(x,y) / J0(x,y)].

There is no explicit R division in this function: using an identical stable R in the numerator and baseline would cancel algebraically, (I_t/R)/(J0/R) = I_t/J0. This cancellation **does not** certify physical attenuation if additive detector offsets, changing illumination or uncertain J0 remain. Positive and negative mean higher/lower signed log contrast, NOT automatically solid versus liquid or chemically calibrated indium concentration.

### A2. Image filtering

The actual morphology-input candidate masks use **Gaussian sigma=1 source pixel**. The implementation performs validity-weighted Gaussian filtering in scipy.ndimage with mode="nearest":

G_t = Gaussian_sigma(P_t * V_t) / Gaussian_sigma(V_t)

only at original-valid pixels with Gaussian validity weight **>=0.999**. This conservatively rejects neighborhoods influenced by invalid pixels. Alternatives explored (but not used by the current front gate) were Gaussian sigma=2, median 3x3 with an all-valid neighborhood, or no filter.

### A3. Binary positive/negative candidates and area opening

Within the provisional ROI and usable pixel domain, define strict-threshold masks:

B_t^+(tau) = 1[G_t > +tau],
B_t^-(tau) = 1[G_t < -tau].

The actual implementation uses **4-connected components** and removes each component with **area <25 pixels** (keeps area >=25). There is no automatic solid filling or phase classification at this stage.

**Do not conflate these exact sources:**

| Candidate purpose | Signed log threshold, Gaussian sigma 1 | Area |
|---|---|---|
| Original positive baseline/red review | +0.04 | >=25 px |
| Expanded positive/solid-zone proxy | +0.02 | >=25 px |
| Negative component candidates used in morphology pilot | -0.04 | >=25 px |

The **amber** expansion is B^+(0.02) minus B^+(0.04): extra low-contrast positive candidates, NOT measured mushy solid fraction. The focused sweep additionally explored positive thresholds 0.025, 0.03, 0.035, 0.05, 0.06, 0.08; negatives 0.04/0.05/0.06/0.08 with area cutoffs 25/75/150. Those alternatives are NOT the morphology pilot's current input.

The targeted-sweep NPY arrays used by the morphology pilot hold five layers, in order: positive_0.02, positive_0.04, positive_0.08, positive_0.02_minus_0.04, negative_0.04.

### A4. Provisional front via morphology

Actual function: envelope(positive_0.02, radius=8, margin=8, median_size=15).

1. Crop the binary expanded-positive mask to the candidate ROI, 292 x 535 source pixels.
2. Binary morphological **closing** with a disk of radius **8 pixels** (swept radii 4,8,12): scipy.ndimage.binary_closing, **border_value=0**. This bridges some branch gaps, and can erode the ROI border. Despite a nearby comment mentioning padding, **no padding is actually performed in the current code**.
3. Label 4-connected components in the closed positive mask.
4. Retain only components intersecting the near-bottom anchor rows starting at local y = max(0,292-(radius+5)) through the bottom. At radius 8 the start is local row **279**, i.e. source y=399. This is a *bottom-connected candidate anchor*, not an independently measured solid–wall boundary.
5. Require >=30 supported image columns **and** >=300 bottom-connected pixels; otherwise return **front unknown / absent**, not a fabricated front. This correctly produced no estimate for main119/main480 under this method; it does not prove absolutely no solidification.
6. In each supported column, take the **topmost** retained bottom-connected pixel: candidate front f_raw(x).
7. **Linearly interpolate** missing column heights (np.interp, constant end extrapolation), then median-filter the resulting height array with width **15**, then Gaussian-filter it with **sigma=2 columns** and nearest-edge mode. The result f(x) is one smooth height per column; underhangs, multiple fronts, narrow cavities and overhangs are not represented faithfully.
8. Construct the **zone envelope** in original source coordinates, Z(x,y) = [pixel in ROI] AND [y >= f(x) - m], **m=8 px** for the reviewed pilot (also swept 0/16). Source y increases downward. This includes the entire region below the provisional front **including liquid channels**; it is NOT an all-solid material mask. The green review line is f(x), while the upper edge of the zone used for retention is at f(x)-m.

No actual 3D reconstruction, physical phase classifier, true liquid-channel graph, additional FillingTransform operation or temporal front smoothing is present in this Python function. Original v25 Wolfram contains Closing/FillingTransform/channel extraction but this is NOT an exact port of that pipeline.

### A5. Negative mask gate — keep entire rooted-looking components

Actual function: keep_connected_negative(negative_0.04, zone, min_overlap=10).

1. Label 4-connected **negative_0.04** components (themselves already >=25 pixels) over native detector coordinates.
2. Count original source pixels in each component C_k that intersect the estimated zone Z.
3. Keep **all pixels of component C_k**, including those extending **above the front**, if its overlap |C_k intersect Z| >= **10 original pixels**.
4. Reject every other complete negative component; cyan = kept, magenta = rejected on the review visualization.

Therefore the rule is:

N_kept = UNION{ C_k : |C_k INTERSECT Z| >= 10 }.

**This is a whole-component geometric support filter, NOT the hard pixelwise crop N∩Z.** It protects plume-like negative branches that extend above the front while connected to the portion in Z. It does NOT yet prove a channel leads to the bulk liquid: mere overlap with Z suffices, even if the overlap is not a true liquid channel.

### A6. Existing results and freshly supplied expert judgment

With front closing disk r=8, upward envelope margin=8, overlap >=10:

| Source frame | Negative raw → retained | Upper diagnostic strip before→after | Central diagnostic window before→after |
|---|---|---|---|
| main1200 | 432→432 | 0→0 | 432→432 |
| main3147 | 8326→6839 | 1698→241 | 6064→6034 |
| end0297 | 8306→8306 | 475→475 | 7257→7257 |

The **new owner report** explicitly says (i) the reconstructed front looks excellent for reviewed examples, (ii) preserving channel-origin plume-like extensions is desired, and (iii) the **magenta rejected components were indeed correctly excluded**. This upgrades the recorded status to *owner visually accepted for shown examples*, **not** independent pixelwise ground truth, absolute phase/solid fraction or universal parameter approval.

Previously swept radius and upward margin sensitivity matters: for main3147 radius8, upper retained negative pixels change from **85 (margin0)** to **241 (margin8)** to **1298 (margin16)**. Freeze r8/m8 as **review example**, not universal optimum.

## B. PROPOSED model — not yet implemented

### B1. Preferred architecture: interpretable component graph before probabilistic model

I recommend **spatial morphology + temporal data association of candidate negative components**, with an optional conditional random field (CRF)/factor graph later if deterministic logic is insufficient. Avoid prematurely fitting probabilities to just six expert-reviewed montage frames.

At each source frame t, preserve original:
- Positive strong and weak candidates, current front f_t(x) and envelope Z_t (or front=unknown).
- Every **pre-gate negative** 4-connected component C_tj.
- Component features: source area and bbox, centroid, principal-axis/elongation, skeleton/branch shape, signed contrast statistics, |C intersect Z| and fraction, front-relative root position, validity/boundary proximity, persistent detector defects, possible true liquid-channel connectivity.

**Spatial coherence must distinguish mere zone overlap from genuine rootedness.** The latter is an independent path through a tentative, source-supported liquid-channel mask into a physically verified bulk-liquid region. It is **not yet computed**; treat it as a soft feature until liquid domain annotations exist. Do not force all below-front areas to solid or all above-front detections to artifacts.

### B2. Temporal links

For every candidate C_tj, consider possible links to components C_(t+1)k within the **same contiguous source-acquisition block**, with:
- real candidate filename delta t (no edges across main ordinals 919/1836/2770 or main/end);
- source-registered displacement/shape/area/contrast changes; motion-compensated component overlap only if the motion field itself is independently verified, otherwise conservative geometric displacement gates;
- candidate split/merge/birth/death: a plume may branch, fragment and reconnect;
- a transient, advected plume may have low fixed-pixel persistence, whereas a detector artifact may be persistently fixed. **Never use temporal persistence alone as a physical truth label.**

A baseline model can promote a plausible plume-like component from spatial-uncertain to temporally-supported if it is matched in, e.g., 2 of 3 neighboring **observed** frames. This is a tunable **hypothesis**, not a physics-derived universal threshold. Use appearance/motion hysteresis to avoid frame-to-frame toggling. Retain short-lived but physically plausible events under an **uncertain** state rather than delete them.

Test four comparable outputs: threshold-only, current spatial-only whole-component gate, temporal-only association, and combined spatial+temporal. Preserve the complete rejected and uncertain ledgers. Dynamic front tracking itself may be smoothed subject to source-timestamp gaps, but must not turn unknown early fronts into fictitious fixed walls.

### B3. Optional structured probabilistic formulation (only after T1 testing)

Let z_i in {plume-like, artifact-like, uncertain} be a *component* label. Define evidence/unary cost U_i(z) from geometry, contrast, image-quality and spatial-root features; temporal neighbor graph E_T based on verified source gaps and motion-gated component associations; optional spatial neighbor graph E_S conditioned on *liquid-channel compatible* edges. A candidate energy is:

E(z)=sum_i U_i(z_i)
     + lambda_t sum_(i,j in E_T) w_ij [z_i != z_j]
     + lambda_s sum_(i,j in E_S) v_ij Phi(z_i,z_j).

This is **a proposed CRF/factor-graph objective, not trained Bayesian posterior, not an implemented optimizer, and not guaranteed appropriate for plume physics**. An HMM suffices for uncomplicated single track; a component graph with split/merge edges handles richer plume topology. Calibrated probabilities require independent source-coordinate labels and held-out sequences.

Literature for *method family*, not direct Ga–In validation: Wang & Ji, 2005 dynamic CRF image sequences; Tsai et al., CVPR 2016 object flow; Li and Zhou, 2014 spatiotemporal superpixel-neighborhood graph cuts; 2024 SFSeg++ spectral space-time graph methods.

## C. Next gates, predeclared tests, and source-locked evidence

1. **Freeze the current morphology baseline and latest user acceptance**: source archive SHA, candidate ROI, +0.02 expanded positive, -0.04 negative, sigma1, 25-pixel area opening, r8/m8 zone, component overlap >=10. Keep old +0.04 review positive unchanged. Distinguish accepted **magenta for shown examples** from ground-truth mask accuracy.
2. **Implement spatial–temporal component graph T1 in an independent new experimental module**; do not silently modify existing PR #20 source/results. Provisional source windows to pre-register before tuning: main 450–700, 1120–1280, 3000–3147; separately end 0–297. All lie within known contiguous source sections. Keep unknown front flags and do not cross acquisition gaps. Measure valid source detector masks, temporal association confidence, component persistence/lineage and front support.
3. **Explicit falsification tests**: a genuine advected plume, a brief physical plume, a split/merge, synthetic missing frames, drifting source registration, stationary detector artifact, static scratches, an isolated upper blob persisting >2 frames, unsupported front, and a plume crossing the front. The accepted user examples constrain: main3147 magenta should stay excluded and central cyan preserved; main1200 all 432 negative candidate pixels preserved; end297 all 8306 preserved. Compare against negative component area-threshold and hard pixel crop.
4. **Report ablations**: raw negative, hard pixel zone cut (diagnostic only), spatial component gate, temporal-only and combined graph, with numeric per-component confusion ledger and uncertainty categories. Include front-position jitter, false upper retained pixels, channel extent retention, pixel motion, inferred lineage, runtime, and param sensitivity. Avoid fitting and evaluating on the same owner-labelled montage panels; obtain a held-out independent annotation set for true recall/precision.
5. **Model acceptance** only after source-registered chamber/sample ROI, independently annotated real liquid/solid and plume structures, verified acquisition chronology and dense frame tests. Actual v25 dynamic temporal MIL remains a separate code validation project. Thermal data and physical indium-composition calibration remain separately blocked until external evidence is available.

**Provenance and workflow:** User-level consent to continue analysis is not approval to merge draft PRs, apply inferred phase labels in production or redistribute raw private TIFFs. No Gmail monitoring was requested. Original numerical benchmark, owner-provided 7z review and full-resolution private X: artifacts remain intact.

This document uses the active Library Tools routing v1.0.4 and Scientific Validation v1.2.0, GitHub Workflows v1.3.0, Scientific Visualization v1.1 and Wolfram Engineering source-fidelity protocols as checked on 2026-11-15.
