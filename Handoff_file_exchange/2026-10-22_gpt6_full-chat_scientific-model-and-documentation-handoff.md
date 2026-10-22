# Research-agent handoff — full conversation synthesis, scientific model, and approved documentation plan

**Date:** 2026-10-22 (Europe/Riga)  
**Agent ID:** ChatGPT-GPT-6 / Mihails-Birjukovs / Coding-Optimization-Docs / solidification-OFV-review  
**Repository:** [Mihails-Birjukovs/Meso-scale_Solidification_Analysis](https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis)  
**Scope:** Complete synthesis of the present research conversation: repository and external-reference audit, published-methods review, calibration provenance, source-code issues, physical assumptions, numerical validation design, user approvals, data-location inventory, and standalone synthetic prototype.  
**Append-only policy:** This is a new dated entry per [README_for_agents.md](README_for_agents.md). Do not edit or delete earlier handoffs. Earlier same-day independent audit: [2026-10-22_chatgpt-gpt6_repository-audit.md](2026-10-22_chatgpt-gpt6_repository-audit.md).

> **Status boundary:** Analysis and provisional *standalone* synthetic tests have been undertaken, but neither active Python source file nor the external 2WCF-SVD repository has been changed. No experimental Ga–In energy balance has been shown to close. Distinguish approved design assumptions from experimentally established facts.

## 1. Corrected scientific and software architecture

This repository originated as the published Mathematica X-ray radiography/solidification pipeline. The current development stage concerns **only**:
- `Python_code/ImagePreprocessWithReference.py`: offshoot of `Dendrite & Plume Analysis v25.nb`, specifically porting/adapting the earlier prototype `Optical Flow -- Image Filtering.nb` to create images suitable for **external 2WCF-SVD**. It also produces optical-density/concentration products for co-registration, but quantitatively calibrated outputs must not undergo arbitrary histogram matching.
- `Python_code/VelocimetryRaksturlielumi.py`: receives 2WCF-SVD sparse vectors and matches them with calibrated X-ray composition fields to reconstruct velocity, vorticity, Q-like invariants, enstrophy/gradient diagnostics, indium fraction, mixture density/viscosity, kinetic energy, and dissipation.

The original `Mathematica_code/Dendrite & Plume Analysis v25.nb` already does solidification-specific segmentation and morphology (liquid/solid, channels, chimney, front, dendrite skeleton/orientation/grains, plume segmentation); retain it as a scientific/methodological reference and possible source of future masks. `Mathematica_code/Optical Flow -- Image Filtering.nb` is filtering-prototype lineage. `Mathematica_code/OFV_field_postprocessing_v2.nb` is an obsolete/mostly check-up notebook; much of its visualization has migrated into the Python postprocessor.

**External OFV engine is strictly read-only**: [pienins/Optical-flow-svd-and-fourier-filtering](https://github.com/pienins/Optical-flow-svd-and-fourier-filtering), specifically `2WCF-SVD_v4_4.py`. Do **not** modify it. Its input loader accepts only `*.tiff`, whereas current Python preprocessing exports `filtered3D_*.tif`; correct the output contract *inside this repo*, after review. The engine exports `velocity_field_%05d.pkl`, keys `x,y,u,v`, and a `parameters.json` with `ArrowDensityStep` and `VelocityInversion`; velocity vectors represent **successive image pairs**, hence should be associated with midpoint times rather than blindly paired by list index to single-frame concentration images.

Read-only source inspection found the upstream OpenCV Farnebäck displacement uses image coordinates, then applies **both** `u_valid = VelocityInversion*u` and `v_valid = VelocityInversion*v` with configured `VelocityInversion=-1`. The downstream script additionally flips `vectors_interp[:,1]` while leaving positions unchanged, and its hold-out validation uses *unflipped* vectors. Physical Cartesian coordinates are x-right/y-up, raw pixel rows y-down; correct signs and derivatives **as a coordinated transformation**, validated on synthetic translations, prior to physical inference.

## 2. Source and literature basis reviewed

- Birjukovs, Shevchenko & Eckert (2023), *An image processing pipeline for in situ dynamic X-ray imaging of directional solidification of metal alloys in thin cells*, *Experiments in Fluids*, 64, 131. DOI: https://doi.org/10.1007/s00348-023-03671-2 . Main article and its accompanying supplementary PDF were attached/reviewed in the conversation. Supplement, Appendix A: dark-current and flat-field correction `(I_raw - <I_dark>)/(<I_beam>-<I_dark>)`; other appendices provide BM3D/NLM, adaptive MIL segmentation, dendrite, plume, concentration-processing parameters. Original paper's scope is predominantly Mathematica solidification analysis; current OFV characterization is a subsequent extension.
- README external links: http://matlink.org/ (MATLink), https://webpages.tuni.fi/foi/GCF-BM3D/index.html#ref_software (BM3D) and DOI above. BM3D now has Python implementations; README's old version is stale. License/compatibility of MATLink/MATLAB BM3D separate from MIT repo.
- `Divergence_Free_Interpolant` is external: https://github.com/Peteris-Zvejnieks/DivergenceFreeInterpolation ; its dense SVD interpolator inverts singular values without an explicit cutoff, creating a conditioning risk for large/near-degenerate vector sets. Compact-support RBF can produce misleading zeros outside observation support. Benchmark against piecewise linear and **regularized unconstrained RBF** with common masks.
- Deflickering methodological reference is the project's previously developed [OOC PIV/PTV documentation](https://mihails-birjukovs.github.io/OOC_Particles_Velocimetry_Docs/), especially `docs/reference/METHODS.md`: choose a reference frame close to typical standardized mean luminance, then histogram-match each frame to it. Use **only on the velocimetry image branch**, never calibrated intensity.

## 3. Natalia Shevchenko calibration correspondence and resolved provenance

Gmail thread `Latest results/progress` dated 2026-08-27 through 2026-09-03: https://mail.google.com/mail/u/?authuser=michael.birjukov%40gmail.com#all/1a0435e9d8601db6 . Natalia supplied `Concentration_mapping_intermediate.docx` and `Concentration_plot.opju` on 2026-09-01; on 2026-09-03 warned that applicability depends on specific X-ray acquisition conditions. The supplied method defines `P=-ln(I/I0)` with the **initial Ga–In melt** as the reference, initial composition 25 **wt.% In**, a Ga-rich channel ~5–10 wt.% and dendrite-rich reference ~98.6 wt.%. Recovered illustrative graph fit `C_In (wt.%) = 156.7 P + 27.0`, `R²=0.9986`.

The Python calibration `C_In_percent = 270.1341*g + 29.2945` is **a different, experiment-specific calibration performed by student Kristofers Rolands Kangīzers for the current velocimetry images**. The user explicitly resolved this; **do not replace the Python coefficients with Natalia's** or treat their difference as a defect. Both describe **indium MASS percentage (wt.%)**, never volume fraction. Record calibration ID, reference-image definition, valid experiment and uncertainty.

Related literature for methods and alloy data (check exact applicability, do not import a paper's numeric calibration blindly): Shevchenko et al. (2015) https://doi.org/10.1016/j.jcrysgro.2014.11.043 ; Kao, Shevchenko et al. (2020) https://doi.org/10.1007/s11837-020-04305-2 ; Shevchenko et al. (2013) https://doi.org/10.1007/s11661-013-1711-1 .

## 4. User-approved physical assumptions (first implementation)

- **Single miscible binary liquid**, Ga–In, Newtonian; the phrase “two-phase miscible” in discussion should not be mistaken for two immiscible fluid phases. All-liquid observation interval for first cropped experiments; solidification may occur elsewhere in the apparatus. Full-cell FOV can correspond to physical stationary **no-slip walls**. Cropped domains are open, with unknown boundary fluxes.
- Gap `h ≈ 0.15 mm` constant; parabolic in-plane Hele–Shaw profile `u_parallel(x,y,z,t) = 6(z/h)(1-z/h) * u_bar(x,y,t)`, impermeable front/back plates. Assume indium concentration `w(x,y,z,t)≈w_bar(x,y,t)` independent of z for now; do not attempt unconstrained through-gap concentration inversion.
- The X-ray radiograph measures integrated attenuation, not velocity. Interpret OFV as an approximation to gap-average `u_bar` when concentration varies primarily in-plane. A previously generated synthetic biased-depth-profile example gave ~16.7% illustrative velocity difference; **do not apply this as a physical correction**. Retain as a sensitivity case. Numerical projection experiments can assess optical-flow bias without inferring unmeasured z structure.
- y **up** for Cartesian physics, gravity `g_vec = -g e_y`, image y **down**; rising plumes upward. Flow buoyancy driven with no other imposed mechanical forcing. Pressure-dilatation work assumed negligible **for now**; test its consistency with mass-continuity diagnostics.
- Temperature dependence `ρ(T,w), μ(T,w)` **deferred**: for now adopt only `ρ(w), μ(w)`. Natalia's top and bottom wall temperatures are not yet available; later one might use an explicitly approximate linear vertical T profile. Direct thermal buoyancy is a named neglected uncertainty, not proof of physical absence.
- Calibrated indium mass fraction `w = C_In(wt.%)/100`. **Density** baseline uses ideal additive-specific-volume law `1/ρ=(1-w)/ρ_Ga+w/ρ_In`. Do not linear-blend density *by mass fraction*. True EOS/excess mixing volumes and temperature corrections postponed.
- **Viscosity**: retain *both* provisional models: (a) volume-fraction linear `μ_L=(1-φ)μ_Ga+φ μ_In`, `φ=(w/ρ_In)/[(1-w)/ρ_Ga+w/ρ_In]`; (b) mole-fraction logarithmic `ln μ_log=(1-x)ln μ_Ga+x ln μ_In`, `x=(w/M_In)/[(1-w)/M_Ga+w/M_In]`. The log model is of literature interest but **not yet a calibrated binary Ga–In property law**. Explore sensitivity; do not assume pure liquid In reference properties are valid below In melting temperature.
- Optical-flow image filtering proposal: reference correction → **Gaussian-model spatiotemporal total-variation filter** → histogram-reference deflickering (OOC PIV pattern). Keep independent unfiltered/minimal, TV-only, TV+deflicker options for controlled tests; assess motion bias. **Never** histogram-match the quantitative calibrated concentration branch.

## 5. Governing physics, identities, and cautions

For barycentric mixture velocity `u`, `∂tρ + ∇·(ρu)=0`, or `∇·u=-(∂tρ+u·∇ρ)/ρ`. Variable *Eulerian* density does **not** imply nonzero divergence: advected heterogeneous density may have `Dρ/Dt=0`. Molecular interdiffusion can produce nonzero barycentric divergence even at low Mach. Alternative volume-average velocity differs from barycentric; OFV measurement's effective meaning needs explicit study. Depth-integrated continuity for constant h and through-gap uniform density: `∂tρ+∇_2·(ρ u_bar)=0`. Evaluate `R_m=∂tρ+∇_2·(ρ u_bar)` before constraining velocity to be solenoidal. A divergence-free interpolator **cannot independently test** physical compressibility because zero divergence is imposed.

Define in-plane gradient `A=∇_2 u`, strain `S=(A+Aᵀ)/2`, spin `Ω=(A-Aᵀ)/2`, vorticity `ω_z=∂xv-∂yu`, `θ=∂xu+∂yv`, `Q_2D=(||Ω||²-||S||²)/2` as a 2D **Q-like**, not full 3D criterion. Keep `G=∫||∇u||²` separate from vorticity enstrophy `Z=(1/2)∫ω²`; their discrepancy is **not** a compressibility test because of boundary effects and planar extensional flows. Examples: solid rotation `(-ay,ax)`; planar extension `(ax,-ay)`; dilation `(ax,ay)`.

For Newtonian flow, primary viscous dissipation is `D=∫τ:∇u`, with shear plus possible dilatational/bulk viscosity. Under incompressible and no-slip full 3D conditions, constant viscosity yields `∫2μ S:S = ∫μ|curl u|²`; for variable viscosity, a gradient correction appears:
`∫2μ S:S - ∫μ|ω|² = -2∫∇μ·[(u·∇)u]` for solenoidal u and no-slip boundary (sign and assumptions important). Cropped domains introduce surface terms, nonzero divergence further terms.

With gap profile `f(z)=6(z/h)(1-z/h)`, `<f>=1`, `<f²>=6/5`, `<f³>=54/35`. If `ρ(w), μ(w)` independent of z and `u=f u_bar`, kinetic energy `K=(6/5)∫A (1/2)ρ h |u_bar|² dA`; dominant gap dissipation `D_gap=∫A (12 μ/h)|u_bar|² dA`; in-plane strain term `D_parallel=(6/5)∫A 2 μ h Sbar:Sbar dA` under solenoidal/shear-only approximation. Depth-integrated squared 3D vorticity is `∫A μh[(6/5)ω_z²+(12/h²)|u_bar|²] dA`. **Do not** identify that vorticity integral with full dissipation without the variable-viscosity and boundary corrections.

Mechanical energy: `K=∫(1/2)ρ|u|²`, potential `E_g=∫ρgy` (upward y), `D=∫τ:∇u`. In stationary **full closed/no-slip** volume with no additional mechanical forcing and negligible pressure dilatation, `d(K+E_g)/dt + D≈0`, conditional on adequate modeling of actual temperature/composition buoyancy and depth-averaged/3D mapping. **Cropped** windows require pressure, advective K+potential, and viscous boundary-work fluxes; pressure reconstructed from the same OFV is not an independent validation signal. Full-cell data better for initial closure. Global energy residual can **reject** inconsistent vectors, not uniquely prove correct OFV (e.g. sign reversals preserve quadratic energies).

Important correction for future derivations: in open domains, combine `K+E_g` with **both** advective and stress-work boundary terms and, where relevant, pressure dilatation; in full gap-integrated dynamics the parabolic flow introduces profile factors in kinetic energy and convective flux. Explicitly distinguish an exact 3D identity from a quasi-2D closure.

## 6. Confirmed or candidate code issues; **do not fix until approved**

`Python_code/ImagePreprocessWithReference.py`:
- Writes filtered concentration parameter JSON into the *unfiltered* folder, and derives some filtered metadata from the unfiltered array (confirmed).
- Possible nonfinite `g_raw=-ln(I_corr)` before safe handling; hard-coded preview index; fixed interactive Windows paths and no batch CLI.
- `filtered3D_*.tif` incompatible with upstream `*.tiff` glob; build an explicit export contract and manifest.
- Confirm quantitative composition reference/crop/frame matching with the currently relevant Kristofers calibration; do not import Natalia's coefficients.
- Strong image enhancements may distort motion; compare minimal, TV and TV+deflicker cases.

`Python_code/VelocimetryRaksturlielumi.py`:
- Upstream `VelocityInversion` plus downstream lone-v-flip; mismatched hold-out train/test conventions; must perform synthetic coordinate translation tests.
- Divergence-free RBF currently hard-selected for all downstream quantities; risk of conditioning, unsupported-region zeros and inability to test divergence independently.
- `N_FRAMES_TO_PROCESS=5`; temporal concentration PKL association by list order, lacking image-pair midpoint timestamp correction.
- Density incorrectly blended linearly in **mass** fraction; revise to reciprocal-specific-volume blend. Keep both μ models and compare uncertainty.
- Shape-based `zoom` for density grid lacks explicit coordinate registration. No flowing **liquid** domain/support mask in full rectangular integrals. In initial cropped interval liquid may fill the crop, but missing/unsupported vectors still require a mask.
- Misnamed `enstrophy_field` stores squared velocity-gradient Frobenius norm; dissipation omits cross-gap shear; `dK/dt + D` cannot close without physical power terms. Add genuine planar Q diagnostic; separate 2D from 3D invariants.
- Preserve per-frame QC, reference calibration, uncertainties, interpolation method/hyperparameters, support masks.

## 7. Approved numerical validation program

**Priority order confirmed by user:**
1. Scientific-model selection, coordinate/mass-conservation conventions, proper calibration metadata;
2. Input/output, frame pairing and spatial registration;
3. Three interpolators (piecewise-linear, regularized unconstrained RBF, divergence-free RBF) with **identical** held-out observations and masks;
4. Kinematics: divergence, vorticity, Q-like, strain, continuity residual, gradient-vorticity identity;
5. Quasi-2D Hele–Shaw gap corrections and closed/open mechanical-energy budgets;
6. Uncertainty, model sensitivity, energy/enstrophy-based independent rejection tests.

Use analytic tests with known fields: rigid rotation `(-ay,ax)` (`θ=0, ω=2a`), planar extension `(ax,-ay)` (`θ=0, ω=0`), and dilation `(ax,ay)` (`θ=2a, ω=0`), plus advected heterogeneous density and projected X-ray parabolic-gap transport. Hold out energy closure **from** interpolation fitting; test scaled, reversed, noisy and otherwise corrupted velocities and report false positives/false negatives. Do not conclude compressibility from gradient/vorticity-square mismatch alone.

## 8. Prototype and datasets

On 2026-10-22, a **standalone, uncommitted-to-repo** test-only prototype was created locally and supplied to user as `ga_in_validation_prototype_2026-10-22.zip`; it contains `MODEL.md`, `README.md`, physics/interpolation/synthetic Python functions, tests and requirements. Earlier conversation reports 17 passing synthetic tests and illustrative errors; these are **not experimental validation** and are not source-repo modifications. The complete prototype may need to be re-provided in a future chat if not available as a live attachment. No real data used to establish energy closure.

Identified shared-Drive data:
- [Kristofers_MSc → Raw Images for MSc](https://drive.google.com/drive/folders/1So6iAgNoLnmcELurrMFBTpYVvWVldLjP): `2011-09-09.7z` (~2.85 GB), `2014-04-04.7z` (~1.51 GB), `2014-04-15-Exp2.7z` (~1.18 GB); candidate full-field raw images (must check actual physical walls, all-liquid interval and reference metadata).
- [2WCF-SVD -- Article → Image_sequences → Solidification](https://drive.google.com/drive/folders/1CHVHJiz8jiAXjUvB6Kw5Sz2AiMZm5Cpi): three small preprocessed solidification image archives, including `20260331_...` (~80 TIFFs, 82x98) and `20260527_...` (~100 TIFFs, 68x170). Archives can be useful for filter comparisons, **not** by themselves sufficient for composition/energy budget.

## 9. Future-work guardrails and deliverables

Current user requests three documentation outputs **before scientific implementation**:
1. This append-only complete chat handoff.
2. Extensive on-repository documentation of current artifacts, published methods, active scripts, exact outstanding issues, planned numerical/physics tests, calibration and file/data interfaces, assumptions, acceptance gates.
3. Standalone pedagogical PDF with careful step-by-step mathematical derivations for 3D mixture and 2D Hele–Shaw reduction, X-ray optical flow assumptions, conversion between fractions and material laws, strain/vorticity/Q, variable-μ identities, continuity and mechanical-energy balance, open/closed controls, depthwise corrections, synthetic validation, uncertainty and limitations.

**Do not alter scientific code or the read-only upstream OFV repo as part of this documentation task.** Earlier handoffs remain intact. In scientific documents, distinguish published facts, user's modeling decisions, mathematical identities, and yet-untested hypotheses.
