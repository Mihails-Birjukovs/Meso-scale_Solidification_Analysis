# Scientific methods and agreed first-stage physical model

**Legend:** **[P]** published/experiment reference; **[C]** visible current-code calculation; **[A]** project-approved model assumption; **[N]** proposed new numerical validation, not yet integrated. For full derivations and sign/boundary details, consult the separately exported pedagogical PDF.

## 1. Radiographs, composition and reference definitions

**[P]** The published 2023 X-ray image pipeline uses dark-current and flat-field correction, schematically
```text
I_corr = (I_raw - <I_dark>) / (<I_beam> - <I_dark>)
```
with morphology and quantitative concentration processing applied to carefully differentiated image products. The exact initial-melt reference and dark correction must match the calibration.

**[C]** The current Python script uses a mean reference field and `g=-ln(I_corr)`. The indium concentration fit used for the current test case is
```text
C_In (wt.%) = 270.1341*g + 29.2945
```
**[A]** This calibration is due to Kristofers for these specific images. Natalia Shevchenko's *separate* three-reference semi-quantitative calibration, `C_In (wt.%)≈156.7P+27.0`, is informative but has different acquisition/reference conditions and **must not overwrite** Kristofers' coefficients.

**[A]** Define indium **mass fraction** `w=C_In(wt.%)/100`. Values outside physical `0<=w<=1` should be counted/flagged as calibration-quality problems prior to an explicitly documented clipping policy.

## 2. Liquid mixture properties

**[A]** Adopt volume-additive mixture density as a first approximation:
```text
v_mix(w)=1/rho(w)=(1-w)/rho_Ga + w/rho_In .
```
Converting to indium volume fraction `φ` and mole fraction `x`:
```text
φ=(w/rho_In)/[(1-w)/rho_Ga+w/rho_In]
x=(w/M_In)/[(1-w)/M_Ga+w/M_In] .
```
Two provisional viscosity models:
```text
mu_linear(w)=(1-φ)mu_Ga + φ mu_In
ln mu_log(w)=(1-x)ln(mu_Ga) + x ln(mu_In) .
```
These are **sensitivity models**, not a fitted Ga–In viscosity law. Temperature dependence is deferred; pure-In liquid endpoint applicability must be justified.

## 3. Mixture conservation and measured velocity

Let `u` denote **barycentric** (mass-average) velocity. Exact local mass continuity:
```text
partial_t rho + div(rho*u)=0
div u = -[partial_t rho + u·grad(rho)]/rho .
```
**[A]** Constant gap `h≈0.15 mm`, impermeable plates, negligible through-gap composition changes, all-liquid initial domain. The gap-averaged mass balance then reads
```text
partial_t rho + div_2(rho*u_bar)=0 .
```
**[N]** Compute `R_m=partial_t rho + div_2(rho*u_bar)` and compare with estimated measurement error; compare div u directly and independently of constrained interpolation. Large time-dependent Eulerian density variations do **not** by themselves imply velocity divergence, because advection can change local density while material density is constant.

**[A]** Standard conservative species equation can be retained for later diffusion modeling:
```text
partial_t(rho*w)+div(rho*w*u + j_In)=0
=> rho*D_t(w)=-div(j_In).
```
A barycentric field may have nonzero divergence due to compositional diffusion even at low Mach number; the volume-average mixture velocity is a different field.

## 4. Gap model and projection assumption

**[A]** Physical axes x-right, y-up, z across the gap. Gravity points downward. Adopt parabolic gap profile
```text
u_parallel(x,y,z,t)=f(z)*u_bar(x,y,t),
f(z)=6(z/h)*(1-z/h) .
```
The profile moments are `<f>=1`, `<f²>=6/5`, `<f³>=54/35`.

**[A]** Assume `w(x,y,z,t)≈w_bar(x,y,t)`. X-ray attenuation is a **line-of-sight integral** `P(x,y,t)=∫_0^h κ(w,T,...)dz`; it is not a velocity measurement. The effective OFV from projected attenuation is treated as a **candidate proxy** for `u_bar`, to be tested with forward synthetic projections. A specially constructed center-weighted through-gap gradient produced an illustrative ~16.7% velocity bias, but this is **not** a universal correction and is **not** applied to real data.

Depth-averaged concentration transport may acquire shear-induced dispersion over time; uniform cross-gap composition is a simplifying first-stage model, not a statement that the true 3D composition must remain uniform forever.

## 5. Differential kinematics

For `u=(u,v)` in x-right/y-up:
```text
A=[[u_x,u_y],[v_x,v_y]],
theta=u_x+v_y,
omega_z=v_x-u_y,
S=(A+A^T)/2, Omega=(A-A^T)/2 .
```
A planar Q-like invariant:
```text
Q_2D=0.5*(||Omega||_F²-||S||_F²)
    = 0.5*(omega_z²/2 - [u_x²+v_y²+(u_y+v_x)²/2]).
```
This quantity is not the full 3D Q criterion because transverse gradient components are unmeasured. Conventional planar vorticity enstrophy `Z_2D=0.5∫omega_z² dA`; velocity-gradient seminorm `G_2D=∫||A||_F² dA` is a **different** diagnostic.

For a smooth flow in domain Ω:
```text
∫Ω ||grad u||²-∫Ω |curl u|²
 = ∫Ω (div u)² + ∮∂Ω [(u·grad)u - u*(div u)]·n .
```
Thus unequal norms do **not** prove compressibility; boundary terms can be nonzero even when div u is identically zero.

## 6. Newtonian viscous dissipation and viscosity gradients

For 3D strain `S=(grad u+grad u^T)/2` and shear viscosity `μ(w)`, the primary dissipative quantity is
```text
D=∫Ω τ:grad u dV .
```
For an incompressible Newtonian model `τ=2μS`, hence `D=∫2μ S:S`.

For full 3D solenoidal velocity, *stationary no-slip boundaries*, and variable μ:
```text
∫ 2μ S:S dV = ∫ μ|curl u|² dV
             -2∫ grad μ · [(u·grad)u] dV .
```
For cropped domains include surface terms; for nonzero divergence include dilatational terms and a specified bulk-viscosity model. The strain formulation is the **primary** dissipation estimate, corrected enstrophy a conditional **secondary** check.

Under depth-parabolic u and z-uniform μ,ρ:
```text
K = (6/5) ∫A 0.5 ρ h |u_bar|² dA
D_gap = ∫A (12μ/h)|u_bar|² dA
D_parallel = (6/5) ∫A 2μh Sbar:Sbar dA    [solenoidal approximation]
∫V μ|curl u|² dV =
∫A μh[(6/5)omega_z_bar² + (12/h²)|u_bar|²]dA
```
The cross-gap term can dominate at h=0.15 mm; the old Python script contains only the in-plane dissipation. The depth-integrated vorticity norm is not generally equal to D for varying μ or non-solenoidal velocity.

## 7. Kinetic plus gravitational potential energy

For a Newtonian barycentric field in 3D with gravitational acceleration `g_vec=-g e_y` and gravitational potential `gy`,
```text
K=∫ 0.5ρ|u|²dV;   E_g=∫ρgy dV .
```
Let `k=0.5ρ|u|²`. Exact fixed-volume total mechanical balance:
```text
d(K+E_g)/dt + D
= -∮[(k+ρgy+p)u - τ·u]·n dS
  +∫ p(div u)dV + P_non-gravitational .
```
With full stationary no-slip walls, no imposed mechanical forcing and negligible pressure dilatation:
```text
d(K+E_g)/dt + D ≈ 0 .
```
**[A]** Treat the latter as an *initial model target*, not an established experimental identity. If directly thermal buoyancy matters, omitting `ρ(T)` can spoil potential-energy closure; the experiment's thermal top/bottom settings are not yet available.

**[N]** A cropped observation rectangle has advective, pressure and viscous boundary-power fluxes. They cannot be set to zero. Pressure inferred from the very OFV being evaluated is *not independent* validation. Depth-averaged energy and fluxes require the profile moments (6/5 for kinetic energy, 54/35 for advective kinetic-energy flux), not an uncorrected planar formula.

## 8. Interpretation: validation versus proof

The intended tool rejects velocity reconstruction methods when well-characterized continuity/kinematic/energy residuals violate physical uncertainty bounds. It does **not** uniquely prove a particular field; quadratic energy quantities can be insensitive to sign reversal or compensate spatial errors. Compare independent held-out vectors, analytic synthetic truth, uncertainty propagation and energy residuals not used in tuning the interpolation.
