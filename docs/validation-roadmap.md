# Approved validation protocol and development roadmap

**Date agreed:** 2026-10-22. **Scope:** Both Python scripts in this repository. External `pienins/Optical-flow-svd-and-fourier-filtering` is **read-only**. Mathematica notebooks are method and mask sources, not candidates for wholesale porting at this stage.

## Target outcome

Build a **composition-aware, quasi-2D, Hele–Shaw velocimetry validation framework** combining:
1. numerical optical-flow/interpolation hold-out error;
2. mixture mass-continuity and independent dilatation assessment;
3. gradient, strain, vorticity, planar Q-like invariants and conditional enstrophy identities;
4. composition-dependent material properties and gap-aware kinetic energy/dissipation;
5. conditional gravitational potential + kinetic energy balance in closed and open control volumes;
6. uncertainty/sensitivity analyses demonstrating *rejection power* against bad velocity fields.

An energy residual can reject inconsististency; it does **not** uniquely establish correct flow.

## Phase 0 — reproducibility and contract audit (highest priority)

**Evidence:** current Python scripts, 2WCF-SVD v4.4 loader/output schema, calibration records, raw reference images, experimental metadata and a representative PKL run.

- Freeze copy of source and 2WCF-SVD *commit SHA* as read-only provenance.
- Record Kristofers' dataset-specific composition fit, reference image, dark-current treatment, crop, acquired frame range, true acquisition fps, time binning and pixel pitch.
- Confirm external input only accepts `.tiff`; add compatible export in active preprocessing source.
- Establish exact mapping from original frames → binned/filtered images → OFV image pairs → pair-center times → concentration fields.
- Establish coordinate-transform test with synthetic right/up/down motions, including upstream `VelocityInversion`. Do not change signs on guesswork.
- Avoid working on unsafe/untrusted PKL inputs.

**Gate G0:** One representative experimental pair passes I/O, coordinate, time and composition provenance audits.

## Phase 1 — image-processing alternatives, quantitative branch unchanged

Hold quantitative `g,C_In` constant for a given experiment and produce *only velocimetry images* under:
- A. Minimal reference correction/normalization;
- B. Gaussian-noise-model spatiotemporal TV;
- C. B + OOC-style histogram reference matching/deflickering.

Configure spatial-vs-temporal smoothing explicitly. Test using known translated/deformed synthetic concentration patterns, optional flicker, noise, finite contrast, true concentration evolution, and if useful synthetic parabolic-gap X-ray projections. Compare:
- endpoint displacement/vector error, signed bias and directional error;
- two-way Farnebäck QC, valid-vector fraction, spatial reliability;
- temporal velocity response/lag and derivative sensitivity;
- spectral/edge distortion and relative preprocessing cost.

**Gate G1:** Select preprocessing variant using an independent synthetic/real-image validation set, not subjective frame appearance. Never histogram-match the calibrated concentration images.

## Phase 2 — three interpolation methods and independent validation

Compare with identical vector observations, physical grid and spatially stratified hold-outs:
1. piecewise-linear interpolation;
2. smooth *regularized unconstrained* RBF;
3. regularized divergence-free RBF.

Use common masks: liquid-domain, sufficient support/nearest-vector distance, geometry, convex hull where applicable, and independently sampled held-out vectors. Record RMSE/MAE, relative RMSE with a declared denominator, angular error, coverage, condition number, support/regularization parameters, compute time and derivative sensitivity. Include synthetic fields:
- solid rotation `(-ay,ax)`: divergence 0, vorticity `2a`;
- planar extension `(ax,-ay)`: divergence 0, vorticity 0;
- dilation `(ax,ay)`: divergence `2a`, vorticity 0;
- smooth vortices, shear layers, irregular missing-data masks and noise.

**Gate G2:** Demonstrate correct component conventions and known-field reconstruction without tuning on the final energy test. Do not pre-select the solenoidal method.

## Phase 3 — mixture transport and kinematic checks

- From calibrated **wt.% In**, derive `w`, `rho(w)`, `mu_linear(w)`, `mu_log(w)`.
- Register `rho` to OFV grid in *physical* coordinates and match to pair-center timestamps.
- Independently evaluate `theta=div(u_bar)` and `R_m=partial_t rho + div(rho*u_bar)`; compare time/space derivative stencils and noise propagation.
- Produce separate `||grad(u)||²`, vorticity enstrophy `omega_z²/2`, strain invariants and 2D Q-like `0.5(||Omega||²-||S||²)`.
- Quantify boundary terms in integral gradient-vorticity identities before drawing compressibility conclusions.

**Gate G3:** Analytical/synthetic continuity residual agrees with model; experimental residual and gradient uncertainty are reported, not interpreted without uncertainty.

## Phase 4 — physically informed Hele–Shaw energy model

**Assumptions:** Newtonian liquid, constant 0.15 mm gap, uniform across-gap composition, parabolic profile, g down, no externally imposed mechanical forcing, rho/mu depend on w only for now; pressure-dilatation assumed negligible pending checking.

- Use parabolic correction `K=(6/5)∫A 0.5 rho h |u_bar|²`.
- Include `D_gap=∫A (12mu/h)|u_bar|²` and in-plane strain contribution with 6/5 weighting under the stated solenoidal approximation; handle dilatation by explicit constitutive assumptions.
- Form `E_g=∫A rho g y h,dA`. Its time derivative is evaluated at correct times. For open crops retain advective, pressure and viscous boundary-work fluxes; flux shape factors differ from unity (`<f³>=54/35` for kinetic convective flux).
- Full physical-cell stationary no-slip domain can use `d(K+E_g)/dt + D ≈ 0` only when pressure dilatation, neglected thermal buoyancy and model/projection uncertainty are bounded.
- Conditional enstrophy cross-check: global variable-viscosity correction, boundary terms and solenoidality assumptions. Strain-based D stays primary.
- Document `rho(T)` thermal buoyancy as omitted. Natalia's top/bottom temperatures are a future input; a linear height-temperature profile is merely an approximation.

**Gate G4:** Synthetic manufactured fields recover expected integrated identities and known terms; reject energy closure claims based on cropped velocities without modeled boundary fluxes.

## Phase 5 — experimental inference and rejection power

- Start with all-liquid true full-physical-FOV raw recordings if suitable; compare with cropped solidification sequences.
- Quantify `R_E=d(K+E_g)/dt+D-P_{nonconservative}+F_{boundary}-P_{p,dilatation}`, with precise sign definitions, and normalize by a predeclared nonzero power scale.
- Explicitly propagate pixel pitch, delta-t, calibration, viscosity-law, gap thickness, missing-vector reconstruction, model profile and finite-difference uncertainties.
- Run deliberately corrupted velocities (reversed, scaled, translated, sparse, noisy, smoothed, local sign inversion) to estimate *detectability* and failure cases. Pure sign reversal is a known blind spot for quadratic energy alone.
- Keep energy residual evaluation on independent frames/cases not used for tuning interpolation/filter parameters.

**Gate G5:** Demonstrate falsification sensitivity and calibrated uncertainty intervals on real data; only then consider a publication-level OFV validity claim.

## Standalone synthetic prototype

A separate temporary `ga_in_validation_prototype_2026-10-22.zip` was produced during conversation. Tests were rerun on 2026-10-22: **17 passed**. It currently implements selected physics functions, Gaussian-kernel RBF comparisons and synthetic invariants. It is **not** merged in this repo and no experimental OFV energy residual has been established. Treat numerical error examples reported in the conversation as *synthetic fixture-specific*, not benchmark performance on Ga–In data.

## Development order and review controls

1. Keep scientific source unchanged until a plan/PR is approved, then work on small isolated branches and reviewable PRs.
2. Lock terminology and units before code refactoring (physical versus image axes, wt.% versus volume fractions, planar versus 3D enstrophy).
3. Ensure any change in calibrated radiometry does **not** inadvertently change the OFV branch and vice versa.
4. Add synthetic regression tests for each physical identity and every resolved source-code bug.
5. Preserve original results and manifests for comparison; report old versus new quantitative outputs explicitly.
6. Do not alter external 2WCF-SVD repo as part of this work.
