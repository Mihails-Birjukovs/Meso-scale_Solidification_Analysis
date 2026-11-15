# Segmentation: original MIL versus new candidate masks

## Published/historical dynamic MIL segmentation

The authoritative historical Mathematica notebook defines per-frame **mean inverse luminance** after its image preprocessing. It uses flat-field correction, Gaussian filtering, image adjustment and inversion to form a scalar time series, then applies a time-series total variation filter.

For frame t with filtered MIL value m[t], the notebook defines its normalized dynamic factor as follows:

~~~text
a[t] = dynamicThresholdBias + 1 - m[t]
F[t] = (a[t] / max(a)) / min(a / max(a))
tau[t] = 1 - thresholdFactor * 10^(-2) * m[t] * F[t]^dynamicThresholdPower
~~~

The v25 saved parameter definitions read: thresholdFactor = **0.85**, dynamicThresholdBias = **3**, dynamicThresholdPower = **15**, solidSegmentSizeThreshold = **25**. The original MILbasedSegmentation function applies Binarize(filtered frame, tau[selected original frame ID]), ColorNegate, then DeleteSmallComponents(...,25). The precise actual runtime choices, filter outputs and selected frame IDs remain case-specific; this page does **not** claim equation-by-equation correspondence to the final journal text without a native publication comparison. See the [2023 journal article](https://doi.org/10.1007/s00348-023-03671-2) and the original v25 notebook.

**This historical dynamic threshold was NOT replaced or altered by the new Python benchmark.** The latter is a separate experiment, not an implementation of the original paper's MIL approach.

## Exploratory signed-contrast candidates, currently in draft PR #20

The case-specific initial specimen baseline J0 is the **pixelwise median of the first 80 original 2014-04-04 experimental frames**, not the separately acquired 111 reference flat fields. Using the operational flat-only branch, with dark-correction experimental alternatives quarantined, compute on valid unsaturated detector pixels:

~~~text
P_t(x,y) = -ln[I_t(x,y) / J0(x,y)]
~~~

Apply validity-weighted Gaussian filtering (sigma=1 source pixel) and reject pixels with filter-neighborhood validity weight <0.999. Work inside the **provisional** ROI rows [120,412), columns [155,690), in a 426 × 761 original detector image. Threshold P at **+0.02** for expanded positive candidates and **-0.04** for negative components, then remove 4-connected components with area <25 pixels. Keep the original +0.04 positive mask as an immutable comparison baseline.

The additional +0.02-but-not-+0.04 positive detections are visually marked as **uncertain/interfacial candidate regions**, not measured solid fraction. Negative intensity changes are not automatically chemically validated plumes.

## Provisional front and negative component retention

1. Binary-close the expanded positive mask using a disk of radius **8 pixels** (sensitivity radii 4, 8, 12).
2. Keep closed positive components touching a near-bottom anchor band (source y ≥399 for the radius-8 example); refuse the front estimate if support <30 columns or <300 source pixels.
3. Take the uppermost retained positive point per supported column; linearly interpolate missing columns; smooth via width-15 median then Gaussian sigma=2 columns.
4. Define the zone below this smoothed front with an **8-source-pixel upward margin**. The zone includes liquid channels and cavities; it is NOT an all-solid pixel mask.
5. Among previously thresholded negative components, keep an **entire** 4-connected component if ≥10 of its original pixels intersect the zone. Reject all other full components.

The method preserves above-front plume-like extensions by retaining whole connected negative components, **not by hard-cropping negative pixels at the estimated front**. It does not yet explicitly verify a physical liquid-channel-to-bulk-liquid path.

For scientific detail consult the [exact PR #20 methods specification](https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis/blob/feat/phase0-2014-04-04-mil-candidate-benchmark-2026-11-14/docs/phase0-2014-04-04-current-mask-pipeline-and-spatiotemporal-design-2026-11-15.md). No public raw radiography sample is embedded in this page.
