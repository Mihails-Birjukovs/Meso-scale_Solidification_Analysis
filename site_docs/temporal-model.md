# Spatiotemporal plume candidates

## Existing spatial-only result

The morphology-derived zone/front is **provisional** but promising. In a source-linked experiment-owner review, the estimated front was judged visually excellent and the discarded **magenta** negative components were correctly excluded. This applies to the shown examples, not all source frames or independent pixelwise masks.

At the radius-8, margin-8 example setting, the main3147 negative mask retained 6,839/8,326 candidate pixels while retaining 6,034/6,064 pixels in the provisional central-channel diagnostic window. Main1200 retained all 432 negative candidate pixels, and end0297 all 8,306. These are code-generated candidate-mask comparisons, **not physical plume recall**. The diagnostic windows and ROI remain unreviewed physical geometry.

## Stage T1 — experimental component graph in draft PR #22, not physically validated

The [experimental T1 v0.1 component graph in draft PR #22](https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis/pull/22) treats each negative-contrast connected component C[t,k] as a node, recording source contrast, centroid, area, elongation, source-pixel mask and **spatial-zone support**. Candidate links currently use source-adjacent frame times, centroid displacement and area/shape gates, with possible split/merge links; they are **not independently validated physical plume lineages**.

The next T1 stage is to validate those links against independent source-coordinate examples, adding motion-predicted shape overlap and birth/death/lineage diagnostics where justified. No source-registered OFV vector field has yet been admitted. Stationary detector artifacts and genuine short-lived advected plumes are opposing stress tests.

**Noise resistance is multi-layered, not only input smoothing.** Gaussian filtering and 25-pixel area opening suppress pixel-scale noise; the morphological zone gate constrains isolated spatial clutter; within T1, robust shape/contrast evidence, track persistence with hysteresis and motion-aware association regularize component decisions. Persistence alone is not plume truth: persistent sensor defects and immobile structures require explicit negative controls.

Acquisition gaps before main ordinals 919, 1836 and 2770 and the separate end stream are **not bridged**. All four predeclared dense windows (main450–700, main1120–1280, main3000–3147, end0–297) have now been source-CRC replayed: **858 frames, 9,397 candidate component nodes and 20,738 proposed links**, not accepted physical trajectories.

A reproducible four-way candidate-mask ablation found **2,250 temporally linked but spatially rejected components**, and **175 morphology-retained but temporally unlinked components**. Thus temporal-only would risk restoring artifacts and hard spatial AND temporal could eliminate brief real events. The safe combined state currently preserves morphology-only decisions and annotates temporal evidence. Source data and methodology are documented in [draft PR #22](https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis/pull/22); this is **not validated segmentation recall, precision or actual plume connectivity**.


### Experimental liquid-channel path hypothesis

A second source-verified PR #22 module flood-fills tentative 2D *not-positive-contrast* paths from the unverified upper liquid ROI through a candidate front to negative optical components. The paths are **not physical fluid-phase truth**. Across 858 frames, the number of morphology-retained components that also had a candidate path with a one-pixel opening was **5,472** using strong-positive +0.04 obstacles but only **4,349** when using the broad-positive +0.02 obstacles. Treating weak positive optical contrast as definitely solid can spuriously disconnect channel-like structures. Neither path definition changes the accepted morphology baseline.

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
