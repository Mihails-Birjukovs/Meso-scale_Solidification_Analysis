# Phase 0 status, MIL source-equation audit and temporal-model mathematics — 2026-11-15

**Scope:** documentation-only review. Scientific source authority: the original Mathematica notebook (v25), current main-branch Python modules and newer experimental candidate-mask code in draft PR #20. No private experimental image is published here.

## Historical MIL and newer contrast masks are DIFFERENT

The source of the published methodology is Birjukovs, Shevchenko and Eckert, *Experiments in Fluids* **64**, article 131 (2023), DOI [10.1007/s00348-023-03671-2](https://doi.org/10.1007/s00348-023-03671-2). The public historical notebook is in Mathematica_code, named Dendrite & Plume Analysis v25.nb, Git blob SHA b13ef6adda22405d89680e3ebe5da50e6f40d297.

Its functions getMILseries, getFilteredMILseries, getDynamicThresholdFactor and MILbasedSegmentation implement, respectively, a mean inverse luminance from flat-corrected/inverted adjusted frames, a total-variation-filtered MIL time series, a normalized dynamic multiplier and the per-frame Binarize/ColorNegate/DeleteSmallComponents segmentation.

For filtered MIL m[t], dynamic bias b, and parameters alpha, p:

~~~text
a[t] = b + 1 - m[t]
F[t] = (a[t] / max(a)) / min(a / max(a))
tau[t] = 1 - alpha * 10^(-2) * m[t] * F[t]^p
~~~

Saved v25 parameter values: alpha = 0.85, b = 3, p = 15, and solid segment size minimum = 25. The notebook applies this tau to its separate allFilteredFrames with a selected-original-frame mapping. This is a **source-transcribed v25 expression**, not yet independently certified identical to the typeset paper equation or a complete native 2014-04-04 experiment replay. Do not silently simplify/remove any original image-adjustment, frame selection or denoising effects.

The later experimental Python contrast masks are a **separate method**, not a modified historical MIL threshold. They compute P = -ln(I/J0) using a specimen baseline J0 formed as the pixelwise median of first 80 original 2014-04-04 experiment frames, Gaussian filtering sigma1 source pixel, and polarity-specific fixed thresholds. Reviewed expanded positive threshold +0.02, historical comparison +0.04, negative input -0.04, minimum 25 pixels per 4-connected component. The 111 Reference TIFFs are detector flat-field recordings, NOT specimen J0. Flat-only is the working correction branch, and dark correction remains quarantined.

The provisional morphology front uses disk closing radius8 on expanded positive, bottom-connected source anchors, a topmost-per-column front, interpolated/median width15/Gaussian sigma2 smoothing, and a zone below that front with upward margin8. A complete negative component is retained if >=10 source pixels overlap the zone, even if the component extends above the front; this is **not** hard pixel cropping and is **not** a verified liquid-channel-to-bulk path.

The experiment owner judged the displayed provisional front excellent and the excluded magenta components correctly removed in shown main1200/main3147/end0297 examples. This is qualitative human review, **not** independent pixelwise phase truth, a proven global optimum or actual concentration calibration. See [draft PR #20](https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis/pull/20) for exact method/source and review ledgers.

## Proposed T1: component graph with noise resilience at multiple layers

**Prior filters** address pixel noise: a validity-aware Gaussian, 25-pixel 4-connected opening and morphology-derived zone selection. **T1 has separate planned regularization:** motion-gated association, shape/contrast consistency, persistence/hysteresis with robust weights, and source-registered artifact priors. Mere persistence is insufficient: stationary detector defects can persist, while real moving plumes can vanish at fixed pixels.

At each observed frame t, make a component graph node i=(t,k) containing signed contrast, mask, centroid c_i, area A_i, elongation, approximate root/front distance and artifact features. For adjacent frames that truly belong to one uninterrupted acquisition, a proposed normalized association cost is

~~~text
d_ij = c_j - c_i - v_i * Delta_t
D_ij = d_ij^T Sigma_ij^{-1} d_ij
Cost_ij = alpha*D_ij
       + beta*(1 - motion_compensated_IoU_ij)
       + gamma*abs(ln(A_j/A_i))
       + delta*shape_distance_ij
~~~

No coefficients have yet been fitted, and unregistered OFV must not supply v_i. Start with a conservative zero-motion model and explicit gating intervals, then validate physical movement. Support split/merge/birth/death and uncertain short-lived candidates. Main source gaps before ordinals 919, 1836 and 2770, and the separate end acquisition, must never be bridged by an unstated interpolation.

## Proposed T2: component conditional random field

A conditional random field (CRF) is a **conditional probability model of the label configuration given the observed image data**. Unlike pixel-wise CRFs, one random variable is assigned per *detected component*: z_i belongs to {plume-like, artifact-like, uncertain}. A generic factor graph is the broader formalism in which a global function is factored into local pieces; it need not be a CRF nor calibrated.

Let X represent all observed source-image and component features. A candidate energy is

~~~text
E(z | X) = sum_i U_i(z_i; X)
       + lambda_t * sum_{(i,j) in E_temporal}
                  w_ij * [z_i != z_j]
       + lambda_s * sum_{(i,j) in E_spatial}
                  v_ij * Phi(z_i,z_j)
~~~

The unary potential U_i scores local evidence (spatial front/zone support, channel origin, brightness/shape, detector artifact risk). Temporal pair factors penalize inconsistent labels **only when an actual motion-compatible association exists**; their weights go to zero at acquisition gaps. Spatial terms should reward physically compatible liquid-channel connections, not smear across the solid/liquid interface. The lambda parameters control how much source evidence may be overridden by regularization; their choice is an independently held-out tuning problem.

If a proper conditional probability model is fitted, then

~~~text
Pr(z | X) = exp[-E(z|X)] / Z(X)
Z(X) = sum_{all label assignments z'} exp[-E(z'|X)].
MAP estimate z_MAP = argmin_z E(z|X).
~~~

The partition function Z is generally expensive for loopy graphs. A minimum-energy label configuration is **not** itself a calibrated posterior probability. For binary attractive pair potentials, a min-cut formulation can sometimes give an exact MAP solution. Three states, split/merge and higher-order channel factors may require justified approximations such as alpha-expansion (only under its energy conditions), belief propagation, or integer optimization.

A simple hidden Markov model on a single well-defined track is a temporal-chain special case; when components split/merge, the explicit graph is more appropriate. A probabilistic CRF or graph provides interpretable uncertainty **only after** a genuinely independent set of labeled source components and a calibration check; colored green/red preference borders on six montages are not such labels.

**Concurrent T2 recommendation:** only a **small synthetic factor-graph feasibility/complexity pilot** should run alongside full T1. Do not fit/deploy two production segmentation algorithms concurrently without sufficient independent ground truth. T1 remains the main development track.

## Source-locked tests and outstanding gates

Proposed dense, gap-safe T1 windows: main 450–700, 1120–1280 and 3000–3147; separately end 0–297. Compare raw threshold-only, morphology-only, temporal-only and combined masks with held-out source frames, reviewer-guided positive and negative examples, and synthetic stationary artifact, deforming/moving plume, transient event and split/merge controls. Preserve uncertainty and exact reasons for each component decision.

The original 2014-04-04 archive SHA256 is 77fac9a38a9cdaa41ee5ec9c9562acb7149ee1cee8f0246a80c2b267928f2510. It contains 111 flat recordings, 3148 main source frames and 298 end frames, original uint16 shape 426×761. The actual source-registered chamber geometry, physical phase boundaries, all-liquid specimen baseline and HZDR thermal chronology still need independent validation. 2014-03-07 remains a distinct mismatched-dimension registration case.

**Documentation-site status:** the public code repository has a separate INM-style Zensical review branch with eight curated source/rights-reviewed text pages, placeholder-free CSS and a strict build pipeline. The site is not deemed deployed merely because CI succeeds. No official INM logo, original TIFF or owner-review image is included.
