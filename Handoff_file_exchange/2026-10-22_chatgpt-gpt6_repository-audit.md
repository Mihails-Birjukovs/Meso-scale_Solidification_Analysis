# Research-agent handoff — repository inventory and code audit

**Date:** 2026-10-22 (Europe/Riga)  
**Agent ID:** ChatGPT-GPT-6 / Alloy-Solidification-Analysis-chat  
**Repository:** [Mihails-Birjukovs/Meso-scale_Solidification_Analysis](https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis)  
**Inspected branch:** `main`  
**Reference HEAD before this report:** `bf0a3ca1257360a84e47d9a25859ec63b71209eb`  
**Scope:** Read-only inspection of repository files; this new handoff file is the only intended GitHub write. No source code was edited, no experiments were rerun, and no computational tests were executed.

## Context for future agents

This project analyzes metal-alloy solidification in quasi-2D Hele–Shaw cells using dynamic X-ray radiography. The current research workflow combines reference-corrected image preprocessing, optical-flow velocimetry (OFV), velocity interpolation and derived flow quantities, composition calibration, solid/liquid segmentation, and moving-front analysis. The main current experiment discussed in ChatGPT concerns eutectic Ga–In and a 2011-09-09 dataset. A separate Python two-way-consistent Farnebäck estimator has been discussed under the name `2WCF-SVD_v4_4.py`, but that file is **not in this repository's inspected main branch**. Its precise version/configuration must be obtained separately before making claims about how the saved OFV vectors were generated.

**Historical working parameters, supported by the present Python scripts:**
- Original pixel spacing `dx0 = 17.5 µm/px`; spatial downsampling factor 4 with OpenCV Lanczos4; nominal effective spacing `dx_eff = 70 µm/px`.
- Original sampling interval `dt0 = 0.2 s` (5 frames/s); non-overlapping temporal averaging in bins of 5; effective sampling interval `dt_eff = 1 s`.
- Cell thickness `d = 0.15e-3 m`.
- Working optical-density definition `g = -ln(I_corrected)` where `I_corrected = image / mean_reference`; preprocessing explicitly notes lack of dark-current correction.
- Empirical concentration calibration `C_In_percent = 270.1341*g + 29.2945`. The provenance and mass-fraction-versus-volume-fraction meaning must be verified against experimental calibration records.
- Prior discussion elected to retain image coordinates `x` right and `y` down for numerical consistency, while separating plot orientation from numerical coordinate transformations.

## Inspected inventory

Ten tracked files in the reference tree:
- `README.md`, `LICENSE`, `.gitattributes`.
- `Handoff_file_exchange/README_for_agents.md` (read in full).
- `Python_code/ImagePreprocessWithReference.py` (read in full; ~982 lines).
- `Python_code/VelocimetryRaksturlielumi.py` (read in full; ~1,311 lines).
- `Mathematica_code/Dendrite & Plume Analysis v25.nb` (~16.7k notebook-file lines; section inventory and selected implementation blocks inspected, **not** each cell exhaustively tested).
- `Mathematica_code/OFV_field_postprocessing_v2.nb` (examined source structure and key interpolation, coordinates, and derived-field portions).
- `Mathematica_code/Optical Flow -- Image Filtering.nb` (examined major filtering and KLD blocks).

Links: [Python preprocessing](https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis/blob/main/Python_code/ImagePreprocessWithReference.py) · [Python velocity analysis](https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis/blob/main/Python_code/VelocimetryRaksturlielumi.py) · [Mathematica solidification analysis](https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis/blob/main/Mathematica_code/Dendrite%20%26%20Plume%20Analysis%20v25.nb).

## Findings — Python image preprocessing

`ImagePreprocessWithReference.py` loads measurement and reference TIFFs, offers interactive crop selection, flat-field corrects via the mean reference image, averages groups of five frames, downsamples spatially by four, calculates optical density, and exports TIFFs and JSON metadata. It has two distinct downstream branches:

1. A quantitative branch for `g`, median + 2D total-variation denoising, and indium concentration maps (both raw and filtered).
2. A more aggressively enhanced image sequence (median/TV/sharpening, tone mapping, squared enhancement, 3D/spatiotemporal TV), useful to test for OFV but not automatically quantitative in intensity.

**Concrete issues to fix or document:**
- Near line 744 the filtered-concentration `concentration_parameters.json` is written to `conc_output_folder` (the unfiltered folder), rather than `conc_filtered_output_folder`. It can overwrite/misplace the metadata for the raw concentration output.
- The filtered-concentration metadata at approximately lines 737–740 derives frame count, shape and extrema from `C_in_percent` rather than `C_in_percent_filtered`. Diagnostic print statements near 700–703 have the same problem.
- `g_raw = -np.log(I_corr)` is computed before safe clipping used for the later downsampled optical density. Invalid normalized pixel intensities can produce nonfinite `g_raw`.
- Plotting `frame_idx = 25` assumes >=26 processed frames.
- Hard-coded local Windows input/output paths and interactive prompts inhibit portable, batch reproducibility.
- No dark-current image subtraction is implemented; the approximation is documented in comments.

## Findings — Python velocity and physical-field analysis

`VelocimetryRaksturlielumi.py` reads concentration TIFFs, `parameters.json` (notably `ArrowDensityStep`), and OFV PKL files with keys `x,y,u,v`. It scales pixel displacements to m/s, constructs a regular sparse-vector grid, diagnoses missing vectors, uses a `Divergence_Free_Interpolant` RBF with `nu=5, k=3, dim=2`, SVD conditioning, and support radius `3*arrow_step`; compares SciPy linear interpolation; performs a 20% hold-out with RNG seed 42; derives field quantities and exports .npy, CSV, and plots. The example run is capped at `N_FRAMES_TO_PROCESS = 5`.

**Highest-priority coordinate consistency issue:**
- At approximately lines 398–432, comments state image coordinates are kept without transformation, but the actual code uses `vectors_interp[:, 1] *= -1` while keeping `positions_interp`, `X_interp`, and `Y_interp` unchanged.
- At approximately lines 506–520, hold-out RBF instead trains/tests with `vectors_all` (unflipped), whereas the production RBF uses `vectors_interp` (flipped). Thus the test does **not evaluate the same exact velocity-component convention as production**. This discrepancy alone does **not** establish the cause of previously reported large relative validation errors. Verify meaning of upstream saved `v` and any `VelocityInversion` applied in the missing OFV estimator before changing signs.
- Reversing only a vector component, without transforming corresponding spatial coordinates, changes divergence and vorticity physics; it is not a neutral coordinate-system change.

**Other relevant technical concerns:**
- No evolving liquid-domain mask is applied to the reconstructed velocity arrays or spatial integrals: current `dV = dx*dy*d` sums over the full rectangular grid.
- `rho_small`, `mu_small`, and `alpha_gallium_small` are shape-matched with `scipy.ndimage.zoom`, not explicitly sampled on the exact OFV coordinate grid; potential half-step/edge misregistration deserves a coordinate-based resampling check.
- The script stores `grad_u_squared = du_dx**2 + du_dy**2 + dv_dx**2 + dv_dy**2` as `enstrophy_field`; standard 2D vorticity-based enstrophy is proportional to `(dv_dx - du_dy)**2`. Keep these two diagnostics separately named.
- The code uses linear mixture expressions for density and dynamic viscosity based on `alpha_in = C_In_percent/100`. Whether the calibrated concentration is a mass or volume fraction must be established; a linear viscosity law is a modeling assumption.
- The Newtonian in-plane dissipation formula implemented is `2*mu*(du_dx**2 + dv_dy**2 + 0.5*(du_dy+dv_dx)**2)`. Thin-gap shear/3D effects and wall friction are not included in that expression.
- `epsilon(t) = dK/dt + D` is a **partial energy-balance residual** and cannot be expected to vanish without accounting for forces, fluxes, moving boundaries, etc.
- There is no importable local `Divergence_Free_Interpolant` module or installation instructions in the inspected repository tree.
- Velocity/concentration file pairing is based on lexically sorted filenames and the minimum list length, with no explicit cross-check of timestamps or original bin indices.

Previous ChatGPT conversation logs reported five-frame 20% RBF hold-out relative RMSE of approximately 247–278%, and small kinetic-energy/dissipation integrals. These are **historical reported outputs, not reproduced results from this repo audit**; verify against the actual data/logs.

## Findings — Mathematica notebooks

- `Dendrite & Plume Analysis v25.nb`: extensive domain segmentation and front analysis already exist. Major identified sections: correction and binning, artifact and solid-mask detection via mean inverse luminance, liquid cavities/channels, `solidificationFront`, `frontHeightMap`, mean front height and vertical displacement dynamics, near-front concentration, dendrite skeleton/orientation/grain decomposition, liquid isolation, plume clustering (configured K-medoids in an inspected block), and report generation. This is a promising source for exporting time-dependent liquid masks to Python. Any exported masks must be aligned in crop, resolution, coordinate convention, and frame timestamps.
- `OFV_field_postprocessing_v2.nb`: imports WXF OFV outputs, flips the vertical **position** via `maxYvalue - y` in `getFormattedData`, and constructs component-wise order-2 `ListInterpolation` objects. The inspected part retains the original vector component values while flipping position, prompting a coordinate audit. Also implements streamline/LIC, vorticity, and divergence visualization. Its regular-grid assembly assumes coordinate combinations are available; test behavior when vectors are missing.
- `Optical Flow -- Image Filtering.nb`: includes 2D filtering, tone mapping, 3D TV, and KLD reconstruction with selected `keepModesIDs = 1;;40`. In the examined Mathematica notebook, 3D TV is applied to `testImagesContrastBoosted`, while Python applies 3D TV to `testImagesEnhanced` (which also includes a squared nonlinearity): the workflows are similar but **not identical**.
- README describes Mathematica + MATLink + MATLAB BM3D prerequisites. The README mentions BM3D v3.0.9, whereas a source block of the larger notebook points to `bm3d_matlab_package_3.0.7`; reconcile requirements.

## Suggested next work (priority order)

1. Obtain the precise upstream `2WCF-SVD_v4_4.py` and associated parameter JSON and representative PKL. Trace sign conventions end-to-end, including `VelocityInversion`, image versus Cartesian axes, plotted arrows, and RBF conditioning/validation.
2. Re-run hold-out interpolation comparison with identically treated train/test coordinates and vectors; examine absolute/relative errors, sensitivity to support radius, and comparisons to linear interpolation. Independent OFV ground-truth validation remains separate.
3. Export Mathematica solid/liquid masks and front positions; match physical calibration, frame indexing, cropping, and coordinate grids; restrict appropriate physical-domain integrals to liquid.
4. Fix preprocessing metadata paths/statistics, finite-value handling, and hard-coded preview frame indices.
5. Give separate, explicit names to vorticity-based enstrophy and gradient-square integrals; review concentration-fraction physics and moving-domain energy terms.
6. Improve reproducibility by documenting Python dependencies and data schema, adding a small synthetic test and provenance manifests for paired concentration/velocity sequences.

## Caveats and handoff policy

This is **source inspection only**. No image data, PKL velocity fields, or notebooks were executed, and no claim about quantitative scientific correctness is established by static reading alone. All line numbers refer to the inspected pre-handoff `main` snapshot; follow links and SHA for reproducibility.

This file is an append-only handoff per `Handoff_file_exchange/README_for_agents.md`. Future agents should **create a new dated Markdown file** instead of editing or deleting this one.
