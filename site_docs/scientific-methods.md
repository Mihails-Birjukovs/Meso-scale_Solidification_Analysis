> **Canonical scientific source:** [`docs/scientific-methods.md`](https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis/blob/main/docs/scientific-methods.md) (Git blob `16844fe3cf435ed118e0e02d36de703e4316aead`). This site edition preserves the source's **[P]/[C]/[A]/[N]** evidence distinctions. Mathematical expressions formerly presented as explanatory text/code fences are transcribed into numbered, accessible LaTeX equations; these are presentation changes only, not a revision of the underlying physical model.

# Scientific methods and agreed first-stage physical model

**Legend:** **[P]** published/experiment reference; **[C]** visible current-code calculation; **[A]** project-approved model assumption; **[N]** proposed new numerical validation, not yet integrated. For full derivations and sign/boundary details, consult the separately exported pedagogical PDF.

## 1. Radiographs, composition and reference definitions

**[P]** The published 2023 X-ray image pipeline uses dark-current and flat-field correction, schematically
$$
I_{\mathrm{corr}}=\frac{I_{\mathrm{raw}}-\langle I_{\mathrm{dark}}\rangle}{\langle I_{\mathrm{beam}}\rangle-\langle I_{\mathrm{dark}}\rangle}
\label{eq:flat-dark-correction}
$$
with morphology and quantitative concentration processing applied to carefully differentiated image products. The exact initial-melt reference and dark correction must match the calibration.

**[C]** The current Python script uses a mean reference field and `g=-ln(I_corr)`. The indium concentration fit used for the current test case is
$$
C_{\mathrm{In}}\,(\mathrm{wt.}\%)=270.1341\,g+29.2945
\label{eq:kristofers-calibration}
$$
**[A]** This calibration is due to Kristofers for these specific images. Natalia Shevchenko's *separate* three-reference semi-quantitative calibration is informative:

$
C_{\mathrm{In}}\,(\mathrm{wt.}\%)\approx156.7\,P+27.0
\label{eq:shevchenko-independent-calibration}
$

It has different acquisition/reference conditions and **must not overwrite** Kristofers' coefficients.

**[A]** Define indium **mass fraction** by

$
w=\frac{C_{\mathrm{In}}(\mathrm{wt.}\%)}{100}
\label{eq:indium-mass-fraction}
$

Physical bounds are

$
0\le w\le1
\label{eq:mass-fraction-bounds}
$

Values outside these bounds should be counted/flagged as calibration-quality problems prior to an explicitly documented clipping policy.

## 2. Liquid mixture properties

**[A]** Adopt volume-additive mixture density as a first approximation:
$$
v_{\mathrm{mix}}(w)=\frac{1}{\rho(w)}=\frac{1-w}{\rho_{\mathrm{Ga}}}+\frac{w}{\rho_{\mathrm{In}}}
\label{eq:volume-additive-density}
$$
Converting to indium volume fraction `φ` and mole fraction `x`:
$$
\phi=\frac{w/\rho_{\mathrm{In}}}{(1-w)/\rho_{\mathrm{Ga}}+w/\rho_{\mathrm{In}}}
\label{eq:volume-fraction}
$$

$$
x=\frac{w/M_{\mathrm{In}}}{(1-w)/M_{\mathrm{Ga}}+w/M_{\mathrm{In}}}
\label{eq:mole-fraction}
$$
Two provisional viscosity models:
$$
\mu_{\mathrm{linear}}(w)=(1-\phi)\mu_{\mathrm{Ga}}+\phi\,\mu_{\mathrm{In}}
\label{eq:viscosity-linear}
$$

$$
\ln\mu_{\mathrm{log}}(w)=(1-x)\ln(\mu_{\mathrm{Ga}})+x\ln(\mu_{\mathrm{In}})
\label{eq:viscosity-logarithmic}
$$
These are **sensitivity models**, not a fitted Ga–In viscosity law. Temperature dependence is deferred; pure-In liquid endpoint applicability must be justified.

## 3. Mixture conservation and measured velocity

Let `u` denote **barycentric** (mass-average) velocity. Exact local mass continuity:
$$
\partial_t\rho+\nabla\cdot(\rho\mathbf u)=0
\label{eq:mass-continuity}
$$

$$
\nabla\cdot\mathbf u=-\frac{\partial_t\rho+\mathbf u\cdot\nabla\rho}{\rho}
\label{eq:mass-divergence}
$$
**[A]** Assume a constant gap, impermeable plates, negligible through-gap composition changes, and an all-liquid initial domain, with

$
h\approx0.15\,\mathrm{mm}
\label{eq:cell-gap-width}
$ The gap-averaged mass balance then reads
$$
\partial_t\rho+\nabla_2\cdot(\rho\overline{\mathbf u})=0
\label{eq:gap-averaged-continuity}
$$
**[N]** Compute `R_m=partial_t rho + div_2(rho*u_bar)` and compare with estimated measurement error; compare div u directly and independently of constrained interpolation. Large time-dependent Eulerian density variations do **not** by themselves imply velocity divergence, because advection can change local density while material density is constant.

**[A]** Standard conservative species equation can be retained for later diffusion modeling:
$$
\partial_t(\rho w)+\nabla\cdot(\rho w\mathbf u+\mathbf j_{\mathrm{In}})=0
\label{eq:species-continuity}
$$

$$
\Longrightarrow\quad \rho D_t w=-\nabla\cdot\mathbf j_{\mathrm{In}}
\label{eq:species-material-derivative}
$$
A barycentric field may have nonzero divergence due to compositional diffusion even at low Mach number; the volume-average mixture velocity is a different field.

## 4. Gap model and projection assumption

**[A]** Physical axes x-right, y-up, z across the gap. Gravity points downward. Adopt parabolic gap profile
$$
\mathbf u_{\parallel}(x,y,z,t)=f(z)\,\overline{\mathbf u}(x,y,t)
\label{eq:gap-parabolic-velocity}
$$

$$
f(z)=6\frac{z}{h}\left(1-\frac{z}{h}\right)
\label{eq:gap-profile-factor}
$$
The profile moments are

$
\langle f\rangle=1
\label{eq:profile-first-moment}
$

$
\langle f^2\rangle=\frac65
\label{eq:profile-second-moment}
$

$
\langle f^3\rangle=\frac{54}{35}
\label{eq:profile-third-moment}
$.

**[A]** Assume

$
w(x,y,z,t)\approx\overline w(x,y,t)
\label{eq:through-gap-composition}
$

X-ray attenuation is a **line-of-sight integral**:

$
P(x,y,t)=\int_0^h\kappa(w,T,\ldots)\,\mathrm dz
\label{eq:line-of-sight-attenuation}
$

It is not a velocity measurement. The effective OFV from projected attenuation is treated as a **candidate proxy** for `u_bar`, to be tested with forward synthetic projections. A specially constructed center-weighted through-gap gradient produced an illustrative ~16.7% velocity bias, but this is **not** a universal correction and is **not** applied to real data.

Depth-averaged concentration transport may acquire shear-induced dispersion over time; uniform cross-gap composition is a simplifying first-stage model, not a statement that the true 3D composition must remain uniform forever.

## 5. Differential kinematics

For `u=(u,v)` in x-right/y-up:
$$
A=\begin{pmatrix}u_x&u_y\\ v_x&v_y\end{pmatrix}
\label{eq:velocity-gradient}
$$

$$
\theta=u_x+v_y
\label{eq:planar-divergence}
$$

$$
\omega_z=v_x-u_y
\label{eq:planar-vorticity}
$$

$$
S=\tfrac12(A+A^{\mathsf T})
\label{eq:symmetric-strain}
$$

$$
\Omega=\tfrac12(A-A^{\mathsf T})
\label{eq:antisymmetric-rotation}
$$
A planar Q-like invariant:
$$
\begin{aligned}
Q_{\mathrm{2D}}=\tfrac12\left(\lVert\Omega\rVert_F^2-\lVert S\rVert_F^2\right) \\
=\tfrac12\left(\frac{\omega_z^2}{2}-\left[u_x^2+v_y^2+\frac{(u_y+v_x)^2}{2}\right]\right)
\end{aligned}
\label{eq:planar-q}
$$
This quantity is not the full 3D Q criterion because transverse gradient components are unmeasured. Conventional planar vorticity enstrophy is

$
Z_{\mathrm{2D}}=\frac12\int\omega_z^2\,\mathrm dA
\label{eq:planar-vorticity-enstrophy}
$

The velocity-gradient seminorm is

$
G_{\mathrm{2D}}=\int\lVert A\rVert_F^2\,\mathrm dA
\label{eq:velocity-gradient-seminorm}
$

It is a **different** diagnostic.

For a smooth flow in domain Ω:
$$
\begin{aligned}
\int_{\Omega}\lVert\nabla\mathbf u\rVert^2\,\mathrm dA-\int_{\Omega}\lvert\nabla\times\mathbf u\rvert^2\,\mathrm dA \\
=\int_{\Omega}(\nabla\cdot\mathbf u)^2\,\mathrm dA+\oint_{\partial\Omega}\left[(\mathbf u\cdot\nabla)\mathbf u-\mathbf u(\nabla\cdot\mathbf u)\right]\cdot\mathbf n\,\mathrm ds
\end{aligned}
\label{eq:gradient-curl-boundary-identity}
$$
Thus unequal norms do **not** prove compressibility; boundary terms can be nonzero even when div u is identically zero.

## 6. Newtonian viscous dissipation and viscosity gradients

For 3D strain `S=(grad u+grad u^T)/2` and shear viscosity `μ(w)`, the primary dissipative quantity is
$$
D=\int_{\Omega}\boldsymbol\tau:\nabla\mathbf u\,\mathrm dV
\label{eq:viscous-dissipation-general}
$$
For an incompressible Newtonian model,

$
\boldsymbol\tau=2\mu S
\label{eq:newtonian-stress}
$

hence

$
D=\int2\mu S:S\,\mathrm dV
\label{eq:incompressible-dissipation}
$.

For full 3D solenoidal velocity, *stationary no-slip boundaries*, and variable μ:
$$
\begin{aligned}
\int 2\mu S:S\,\mathrm dV=\int\mu\lvert\nabla\times\mathbf u\rvert^2\,\mathrm dV \\
\qquad-2\int\nabla\mu\cdot\left[(\mathbf u\cdot\nabla)\mathbf u\right]\,\mathrm dV
\end{aligned}
\label{eq:variable-viscosity-identity}
$$
For cropped domains include surface terms; for nonzero divergence include dilatational terms and a specified bulk-viscosity model. The strain formulation is the **primary** dissipation estimate, corrected enstrophy a conditional **secondary** check.

Under depth-parabolic u and z-uniform μ,ρ:
$$
K=\frac65\int_A\frac12\,\rho h\lvert\overline{\mathbf u}\rvert^2\,\mathrm dA
\label{eq:parabolic-kinetic-energy}
$$

$$
D_{\mathrm{gap}}=\int_A\frac{12\mu}{h}\lvert\overline{\mathbf u}\rvert^2\,\mathrm dA
\label{eq:gap-dissipation}
$$

$$
D_{\parallel}=\frac65\int_A2\mu h\,\overline S:\overline S\,\mathrm dA\qquad\text{(solenoidal approximation)}
\label{eq:inplane-parabolic-dissipation}
$$

$$
\begin{aligned}
\int_V\mu\lvert\nabla\times\mathbf u\rvert^2\,\mathrm dV \\
=\int_A\mu h\left[\frac65\,\overline\omega_z^2+\frac{12}{h^2}\lvert\overline{\mathbf u}\rvert^2\right]\,\mathrm dA
\end{aligned}
\label{eq:gap-vorticity-integral}
$$
The cross-gap term can dominate at h=0.15 mm; the old Python script contains only the in-plane dissipation. The depth-integrated vorticity norm is not generally equal to D for varying μ or non-solenoidal velocity.

## 7. Kinetic plus gravitational potential energy

For a Newtonian barycentric field in 3D with gravitational potential \(gy\) and downward gravitational acceleration,

$
\mathbf g=-g\,\mathbf e_y
\label{eq:gravitational-acceleration}
$,
$$
K=\int\frac12\rho\lvert\mathbf u\rvert^2\,\mathrm dV
\label{eq:kinetic-energy-volume}
$$

$$
E_g=\int\rho gy\,\mathrm dV
\label{eq:gravitational-potential-energy}
$$
Let

$
k=\frac12\rho\lvert\mathbf u\rvert^2
\label{eq:kinetic-energy-density}
$

The exact fixed-volume total mechanical balance is:
$$
\begin{aligned}
\frac{\mathrm d(K+E_g)}{\mathrm dt}+D \\
=-\oint\left[(k+\rho gy+p)\mathbf u-\boldsymbol\tau\cdot\mathbf u\right]\cdot\mathbf n\,\mathrm dS+\int p(\nabla\cdot\mathbf u)\,\mathrm dV+P_{\mathrm{non\text{-}gravitational}}
\end{aligned}
\label{eq:mechanical-energy-balance}
$$
With full stationary no-slip walls, no imposed mechanical forcing and negligible pressure dilatation:
$$
\frac{\mathrm d(K+E_g)}{\mathrm dt}+D\approx0
\label{eq:closed-mechanical-model-target}
$$
**[A]** Treat the latter as an *initial model target*, not an established experimental identity. If directly thermal buoyancy matters, omitting `ρ(T)` can spoil potential-energy closure; the experiment's thermal top/bottom settings are not yet available.

**[N]** A cropped observation rectangle has advective, pressure and viscous boundary-power fluxes. They cannot be set to zero. Pressure inferred from the very OFV being evaluated is *not independent* validation. Depth-averaged energy and fluxes require the profile moments (6/5 for kinetic energy, 54/35 for advective kinetic-energy flux), not an uncorrected planar formula.

## 8. Interpretation: validation versus proof

The intended tool rejects velocity reconstruction methods when well-characterized continuity/kinematic/energy residuals violate physical uncertainty bounds. It does **not** uniquely prove a particular field; quadratic energy quantities can be insensitive to sign reversal or compensate spatial errors. Compare independent held-out vectors, analytic synthetic truth, uncertainty propagation and energy residuals not used in tuning the interpolation.
