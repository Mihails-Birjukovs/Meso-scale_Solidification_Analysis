# Spatiotemporal plume candidates

## Existing spatial-only result

The morphology-derived zone/front is **provisional** but promising. In a source-linked experiment-owner review, the estimated front was judged visually excellent and the discarded **magenta** negative components were correctly excluded. This applies to the shown examples, not all source frames or independent pixelwise masks.

At the radius-8, margin-8 example setting, the main3147 negative mask retained 6,839/8,326 candidate pixels while retaining 6,034/6,064 pixels in the provisional central-channel diagnostic window. Main1200 retained all 432 negative candidate pixels, and end0297 all 8,306. These are code-generated candidate-mask comparisons, **not physical plume recall**. The diagnostic windows and ROI remain unreviewed physical geometry.

## Stage T1 — approved, not yet validated

The proposed component-graph method treats each negative-contrast connected component C[t,k] as a node, with observed contrast, centroid, area, elongation, boundary distance, source-pixel mask, front-relative position, and explicit **spatial-zone support**.

Add gated associations between nodes of consecutive acquisition frames, using source-time differences, expected displacement, shape similarity and optionally motion-compensated overlap. Keep split, merge, birth and death events explicit; stationary detector artifacts and genuine short-lived advected plumes are opposing stress tests.

**Noise resistance is multi-layered, not only input smoothing.** Gaussian filtering and 25-pixel area opening suppress pixel-scale noise; the morphological zone gate constrains isolated spatial clutter; within T1, robust shape/contrast evidence, track persistence with hysteresis and motion-aware association regularize component decisions. Persistence alone is not plume truth: persistent sensor defects and immobile structures require explicit negative controls.

Temporal gaps in the main 2014-04-04 series before zero-based ordinals 919, 1836 and 2770, and the separate end stream, must **not** be bridged without registered acquisition timing. Test proposed dense windows main 450–700, 1120–1280 and 3000–3147, plus end 0–297 independently.

Compare original threshold-only, morphology-only, temporal-only and morphology+temporal components with source-linked reasons for every kept, rejected or uncertain detection. The T1 implementation and dense-source evidence have **not** yet been accepted.

## Optional T2 — component conditional random field / factor graph

Let each component i have label z_i in {plume-like, artifact-like, uncertain}. The proposed energy is

~~~text
E(z) = sum_i U_i(z_i)
     + lambda_t * sum_(i,j in temporal_edges) w_ij * [z_i != z_j]
     + lambda_s * sum_(i,j in spatial_edges)  v_ij * Phi(z_i,z_j)
~~~

The unary term U_i encodes each component's observation evidence: morphology, contrast, channel rooting and artifact likelihood. Temporal-edge weights w_ij represent confidence in linking motion-consistent component instances over time. Spatial edges may encode physical channel-network compatibility, **not** indiscriminate smoothness over the solidification interface. Minimize E for a maximum-a-posteriori label configuration if potentials define a probability model; otherwise interpret it strictly as regularized energy minimization.

A normalizing partition function Z=sum_z exp[-E(z)] would be needed to interpret p(z|images)=exp[-E(z)]/Z as a conditional probability. Neither potentials nor probabilities are trained or calibrated at this stage. Splits/merges and transient plumes require care; a simple HMM is sufficient only for isolated tracks.

**Recommended sequence:** implement interpretable T1 and a small synthetic T2 feasibility benchmark in parallel *only as an independent research test*. Do not concurrently implement both full production models or fit a CRF on six visually marked montages.
