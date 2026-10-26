# 2026-10-27 — Ga–In density reconstruction: mass-fraction fix

**Agent:** ChatGPT (GPT-6) working with Kristofers Rolands Kangīzers  
**Repository:** `Mihails-Birjukovs/Meso-scale_Solidification_Analysis`  
**Branch:** `fix/ga-in-density-mass-fraction-2026-10-27`  
**Scope:** one scientific formula correction in `Python_code/VelocimetryRaksturlielumi.py`.

## Context

The project's calibrated indium field is `C_in_percent` in **wt.%**, so the legacy variables `alpha_indium = C_in_percent / 100` and `alpha_gallium = 1 - alpha_indium` represent **mass fractions** (after the pre-existing clipping step), not volume fractions.

The previous implementation directly interpolated pure-component densities:

```python
rho = (alpha_gallium * rho_gallium + alpha_indium * rho_indium)
```

This would be the volume-fraction mixing rule, not the mass-fraction rule.

## Change

Under the first-stage assumption of additive component volumes, reconstruct mixture density from mass-weighted *specific volumes*:

```python
rho = 1.0 / (alpha_gallium / rho_gallium + alpha_indium / rho_indium)
```

Added two comments documenting the wt.% basis and additive-volume assumption. The existing viscosity calculation is **not changed**; its constitutive-law choice remains open (see issue C13 in `docs/known-issues.md`). No image calibration coefficients, optical-flow procedures, flow interpolation, energy equations, or input/output paths were modified.

This narrowly addresses **C03** in `docs/known-issues.md`. The October 22 issue register is an intentionally dated baseline, not rewritten here.

## Verification and limits

- Synthetic check: at `w_In=0`, `rho=5904 kg/m^3`; at `w_In=1`, `rho=7310 kg/m^3`.
- At `w_In=0.25`, corrected `rho=6202.233239922397 kg/m^3`, compared with the previous `6255.5 kg/m^3`.
- The corrected formula stays between endpoint densities for physically valid fractions and positive endpoints.
- The real experimental pipeline was **not run**, because the referenced TIFF/PKL inputs use a local Windows filesystem unavailable in this GitHub review.
- The code still clips the concentration-derived fractions before reconstructing properties; the calibration QC policy, fraction naming, mixture nonideality, temperature-dependent densities and viscosity mixture model require separate assessment.

## Continuity instructions

Preserve this file as an append-only handoff. Verify the change against experiment-specific input data before attributing improvements in downstream kinetic-energy or mass-continuity diagnostics to it. Do not claim that the energy budget is closed: known issues C04/C05/C06 and others remain open.
