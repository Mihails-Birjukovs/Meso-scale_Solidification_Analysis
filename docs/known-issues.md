# Confirmed issues, physical limitations and uncertainty register

**Baseline:** 2026-10-22. **No source fixes have been made.** Severity is based on potential scientific impact, not a claim that every discrepancy has already affected published results. Line numbers refer to October 2026 source and may shift.

## Severity terminology

- **P0 — scientific blocking:** must resolve before interpreting quantitative experimental closure as evidence of valid OFV.
- **P1 — high:** definite defects/incompatibilities or major reproducibility limitations.
- **P2 — follow-up:** robustness, efficiency, documentation and optional scientific refinements.

| ID | Severity | Component | Evidence | Required resolution / independent verification |
|---|---|---|---|---|
| C01 | P0 | `VelocimetryRaksturlielumi.py` | `vectors_interp[:,1]*=-1` with unchanged y coordinate; holdout uses raw `vectors_all` | Trace upstream `VelocityInversion` on synthetic directional images and enforce consistent x-right/y-up transform through data, derivatives and plots |
| C02 | P0 | OFV-field reconstruction | Divergence-free RBF selected before testing whether projected barycentric velocity is solenoidal | Compare linear, regularized unconstrained RBF and divergence-free RBF with identical train/test split and masks; test variable-density continuity |
| C03 | P0 | Quantitative physical field | Current `rho=alpha_Ga*rho_Ga+alpha_In*rho_In` uses **mass fraction** for a volume-additive density approximation | Change later to reciprocal density after checking calibration and pure-component property values |
| C04 | P0 | Physics energy | `dK/dt + D` omits gravity/potential, gap wall shear and cropped-boundary mechanical flux | Derive/test full control-volume budget with physical masks; do not label the old residual 'energy closure' |
| C05 | P0 | Calibration/time registration | Index pairing between concentration TIFFs and velocity PKLs ignores velocity image-pair midpoint times | Explicit source IDs, bin times, dimensions, crop origin, pixel pitch and global sign conventions |
| C06 | P0 | Full-domain physics | Interpolation support/missing-observation masking not used consistently in physical-volume sums | Integral only on valid liquid/support region or derive an explicit extrapolation uncertainty |
| C07 | P1 | `ImagePreprocessWithReference.py` | Filtered concentration JSON written into unfiltered folder (~line 744) | Fix output path and verify per-product JSON metadata |
| C08 | P1 | Same | Filtered concentration extrema/count/shape metadata use unfiltered array | Use filtered array for filtered-product metadata; regression test |
| C09 | P1 | Input/output | Local `filtered3D_*.tif` versus external 2WCF-SVD `*.tiff` loader | Output compatible `.tiff`; do not change external repo |
| C10 | P1 | Radiometry | `g_raw=-ln(I_corr)` before safe handling of zero/negative intensities | Check finite/positive input with explicit invalid mask and QC fractions |
| C11 | P1 | Reconstruction numerical conditioning | External compact-support divergence-free RBF dense SVD has no robust singular-value regularization in inspected package version | Record conditioning, regularization, support effects and solve diagnostics; benchmark alternatives |
| C12 | P1 | Measurement interpretation | X-ray projected OFV is not proven gap-average barycentric velocity | Compare with synthetic forward projections of parabolic gap flow; treat identity as approximation and propagate uncertainty |
| C13 | P1 | Constitutive model | `mu` is currently a naive linear mass-fraction blend | Use selectable **volume-linear** and **mole-logarithmic** provisional models; compare sensitivity to uncertainty; later seek measured Ga–In properties |
| C14 | P1 | Physics nomenclature | `enstrophy_field` is `||grad u||_F²`, not `omega²/2` | Export named gradient seminorm, vorticity enstrophy and Q-like field separately |
| C15 | P1 | Cross-gap flow | Thin gap h=0.15 mm; in-plane-only dissipation misses potentially dominant plate shear | Include `D_gap` and 6/5 velocity-profile corrections; bound profile applicability |
| C16 | P1 | Model completeness | Temperature difference known to exist but thermal density contribution unavailable | Keep `rho(w)` for now; flag omission explicitly and seek top/bottom temperatures from Natalia, with optional linear T(y) approximation |
| C17 | P2 | Input config | Hard-coded local paths and interactive prompts, fixed previews, five-frame limit | Data manifest, CLI or config, parameter validation, headless tests |
| C18 | P2 | Registration | `zoom` grid-size matching without explicit calibration transforms | Interpolate to physical x/y coordinates and test half-pixel/edge offsets |
| C19 | P2 | Filtering | Strong enhancement, TV and deflickering may bias true apparent motion | Three-way controlled filter comparison, including synthetic endpoint error and temporal velocity bias |
| C20 | P2 | Domain dynamics | Initial crop is fully liquid; future frames may develop solid | Start with all-liquid; later export registered solid/liquid masks and moving-front position from Mathematica |
| C21 | P2 | Documentation/provenance | Mathematica comments/defaults can differ from assigned parameter values | Persist effective execution parameters per experiment and inspect before publication |
| C22 | P2 | Security/data | PKL serialization loads arbitrary Python objects | Use trusted PKL only or safer array interchange |
| C23 | P2 | Licensing | MATLAB BM3D/MATLink scientific limitations and source version uncertainty | Document third-party license/version; avoid bundling without rights |

## Confirmed facts that are *not* bugs

1. Kristofers' current-test calibration `C_In(wt.%)=270.1341*g+29.2945` differs intentionally from Natalia's separate-run fit. Do **not** silently replace the former.
2. Local images are cropped intentionally to select an all-liquid time/FOV interval. Their boundaries are **not** no-slip walls. Only genuine full-FOV physical walls can be modeled as stationary no-slip.
3. Use of `rho(w),mu(w)` neglecting `T` is an approved **first-stage simplification**; thermal buoyancy remains a later uncertainty.
4. Uniform concentration across the gap and OFV equal to gap-average motion are working approximations, not verified universal facts.
5. Two viscosity models are provisional sensitivity laws; no authoritative binary Ga–In fit has yet been selected.

## Uncertainty register

| Quantity | Primary uncertainty | Suggested diagnostic |
|---|---|---|
| X-ray density `rho(w)` | calibration coefficient, reference normalization, basis wt.%, radiographic thickness/depth weighting, mixture EOS | source/reference audit, calibration uncertainty Monte Carlo |
| Velocity `u_bar` | displacement error, missing vectors, pixel/time scale, sign, depth-projection bias | synthetic known translations, OFV QC and independent holdout |
| Derivatives `grad u` | interpolation smoothing, support radius, differentiation boundary errors | mesh refinement, method comparison, divergence/identity tests |
| Viscosity `mu(w)` | choice of mixing law and reference material values | two-model sensitivity envelope |
| Gap `h` | plate separation, uniformity, effective profile | geometry uncertainty; `D_gap∝1/h` after area integration |
| Mechanical energy | crop flux, unknown pressure, time differentiation, gravity direction, temperature-dependent buoyancy | closed-full-cell sequence, independent pressure/source or bounded residual, ensemble uncertainty |
| Image filtering | genuine solute transport versus flicker, space-time smoothing scale | minimal/TV/TV+deflicker controlled comparisons |

## Must-not-pass acceptance gates

- Do **not** use near-zero divergence from a divergence-free RBF as evidence that the true flow is incompressible.
- Do **not** deduce compressibility from `∫||grad u||² -∫omega²` without boundary and constitutive terms.
- Do **not** claim viscous dissipation from planar derivatives alone represents 3D thin-gap dissipation.
- Do **not** compare a velocity defined at a pair midpoint with an arbitrary concentration image and call the resulting continuity residual physical.
- Do **not** fit interpolation using the mechanical-energy residual and subsequently cite that same residual as an independent validation.
- Do **not** treat low global energy residual as a unique proof of correct velocity, especially with unknown pressure flux.
- Do **not** transfer a calibration across X-ray acquisition conditions without verification.

## Tracking status

This register is documentation only, not a set of new GitHub Issues or an indication that fixes have been committed. Link each future issue/PR to the corresponding ID and synthetic/experimental acceptance test, while preserving the handoff ledger.
