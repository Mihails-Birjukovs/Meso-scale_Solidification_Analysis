# Current source inventory and methods lineage

**As inspected:** `main`, 2026-10-22. This page documents **existing** source behavior. Future intended behavior is kept separate in [the roadmap](validation-roadmap.md). Static source inspection does not establish that any experimental result has been reproduced.

## 1. Top level

- `README.md`: Mathematica-origin short description; BM3D/MATLink prerequisites, publication and feature outline. The MATLAB BM3D version mention is historical. 
- `LICENSE`: MIT software license; does not extend automatically to third-party algorithms or experimental images.
- `.gitattributes`: repository attributes.
- `Handoff_file_exchange/`: append-only dated agent reports. See [the handoff protocol](../Handoff_file_exchange/README_for_agents.md).
- `Mathematica_code/`: three notebooks.
- `Python_code/`: two scripts, the planned active targets.

## 2. Mathematica: published domain-analysis notebook

[**Dendrite & Plume Analysis v25.nb**](../Mathematica_code/Dendrite%20%26%20Plume%20Analysis%20v25.nb) implements a substantial X-ray processing pipeline for thin-cell alloy solidification. Consult the [2023 paper and supplementary material](references-data.md) for the *methodological* account; the notebook encodes experimental choices, intermediate visualization and custom notebook-state variables.

Identified methodological stages:
1. Raw radiographs, crop/flat-field correction, optional time filtering and artifacts.
2. Mean inverse luminance (MIL), adaptive solid/liquid partitioning and solid-fill factor.
3. Solid-domain opening/closing, liquid cavities and channels (chimneys).
4. Solidification-front extraction, shape, height, motion and regional concentration.
5. Solid dendrite preprocessing, skeleton extraction, crossing resolution.
6. Local orientation maps, spectral peaks, assignment/decomposition into grains by orientation and proximity.
7. Liquid-region analysis, concentration estimates and convective plume segmentation, with report-style visualizations.

**Source/documentation discrepancy:** some notebook comments contain example/default parameter values different from adjacent assignments (e.g. `liquidArtefactScale`, `channelClosingScale`, a hard-coded upper front-frame limit). The effective assigned values and experiment ID must be recorded when reproducing a figure.

**Scientific status:** The 2023 peer-reviewed paper supports the underlying methodology; this specific notebook has not been executed during this audit. No Python port of all grain-analysis methods is planned at the current stage.

## 3. Mathematica: historical OFV prototyping

[**Optical Flow -- Image Filtering.nb**](../Mathematica_code/Optical%20Flow%20--%20Image%20Filtering.nb): historical development of 2D and spatiotemporal filtering, nonlinear contrast enhancement and Karhunen–Loève/SVD mode selection. The Python implementation was adapted from this work, but the exact order and transforms are not identical. It is a **reference**, not an authoritative specification of current Python output.

[**OFV_field_postprocessing_v2.nb**](../Mathematica_code/OFV_field_postprocessing_v2.nb): earlier WXF-based velocity-field import, interpolation, streamline/LIC and derivative visualization. Most practical postprocessing and visualization has migrated to `VelocimetryRaksturlielumi.py`; this notebook is mostly an exploratory check-up legacy artifact. Its vertical **position** transform differs from the downstream Python vertical **vector** flip: neither should be copied blindly without verifying the upstream velocity convention.

## 4. `Python_code/ImagePreprocessWithReference.py`

[Source](../Python_code/ImagePreprocessWithReference.py)

This is an interactive procedural analysis script (~980 lines, local Windows paths) originally forked from the published radiographic treatment and inspired by the image-filter notebook.

### Current operations

- Enumerates cropped/raw TIFF images and reference TIFFs.
- Crops source and reference to user-defined field of view, creates experiment-specific output folders.
- Forms an averaged reference, normalizes input intensities and flags problematic pixels.
- Computes raw optical density `g_raw=-ln(I_corr)` and emits diagnostics.
- Time-averages nonoverlapping bins (currently five frames) and downsamples images spatially (currently fourfold).
- Computes `g_downsampled=-ln(I_corr_downsampled_safe)`, and experiment-specific `C_In_percent=270.1341*g_downsampled+29.2945`, with a separate filtered concentration output.
- Builds an enhanced/3D-TV-filtered image stack, exports `filtered3D_%05d.tif` and JSON parameter snapshots.
- Provides intermediate images (`gRaw`, `g_preprocess`, `Conc_In`, `binnedImages` etc.) and operator-controlled subfolder names.

**Quantitative versus motion-image interpretation:** raw/corrected optical density is meant to support calibration; aggressively filtered/enhanced images are *candidate* motion-estimation inputs. They need not retain the intensity scale used for concentration reconstruction.

### Concrete existing defects / limitations

- Filtered concentration metadata JSON is written into the unfiltered concentration folder; statistics in that metadata mistakenly reference unfiltered arrays.
- The raw logarithm may encounter zero/non-positive intensities before later safety clipping.
- Uses fixed preview frame indices and interactive top-level prompts.
- Writes `*.tif` images whereas the **external** 2WCF-SVD v4.4 loader searches `*.tiff`.
- Does not have a complete manifest connecting source frames, calibration ID, reference kind, filtering transforms and exported frame timestamps.
- Exact dark-current correction differs from the paper's optional/reference procedure: the present script explicitly notes the absence of dark-current subtraction.

### Scientific issues not automatically bugs

Taking `-⁠ln(mean(I))` rather than `mean(-ln(I))` yields different values through Jensen's inequality; this must be validated against *the selected calibration definition*, not arbitrarily changed. TV/deflickering/sharpening may improve OFV consistency or may distort motion; compare in controlled tests.

## 5. `Python_code/VelocimetryRaksturlielumi.py`

[Source](../Python_code/VelocimetryRaksturlielumi.py)

Current procedural script (~1310 lines):
- Reads an external `parameters.json`, `velocity_field_*.pkl` with keys `x,y,u,v`, and `Conc_In_*.tif` via nominal numerical filename ordering.
- Uses nominal pixel/time scale, creates valid/absent vector masks and sampling diagnostics; example `N_FRAMES_TO_PROCESS=5`.
- Conditions a compact-support `Divergence_Free_Interpolant` RBF on sparse points and builds a dense regular field; compares a SciPy piecewise-linear field.
- Performs a 20% seeded hold-out of sparse vectors, but validation convention currently differs from production.
- Resamples Ga and In fractions, density and viscosity to the reconstructed field, derives velocity magnitude, divergence, vorticity, a gradient-squared field labeled 'enstrophy', in-plane viscous dissipation, kinetic-energy density and domain sums.
- Exports `.npy`, plots and summary tables.

### Present numerical and physical limitations

The production path flips `v` without the matching y-coordinate transform, yet the hold-out uses original vector convention. Its default external estimator has already multiplied both `u,v` by `VelocityInversion`. The resulting Cartesian meanings of gradients are not established.

The script assumes solenoidal interpolation, then computes divergence of that constrained field; this is not an independent compressibility observation. It lacks source-vector confidence weights, regularization/convergence diagnostics and integration-domain masking of unsupported areas. The compact-support RBF can produce zero predictions outside observation neighborhoods. The upstream interpolation library's dense SVD path can be ill-conditioned.

The density law currently linearly interpolates **mass-fraction** densities rather than additive specific volumes. Viscosity currently also uses a linear mass-fraction blend; both will become explicit constitutive model choices. It calculates in-plane-only dissipation and ignores cross-gap shear; it has no explicit calculated planar Q field and mislabels squared Frobenius gradient norm as enstrophy.

Density/velocity co-registration currently depends on shape-based `zoom`, not an explicit shared physical grid. Energy calculations over the rectangular field assume every pixel represents valid liquid, use `dV=dx*dy*h`, and omit buoyancy/potential, flux and pressure/dilatation terms. These are **not yet trustworthy mechanical-energy closure diagnostics**.

## 6. Tested prototype versus production source

A standalone uncommitted synthetic suite, `ga_in_validation_prototype_2026-10-22.zip`, was created in this chat and retested: **17 tests passed**. It exercises analytical rotation/extension/dilation, mass-fraction laws, projected-profile effects, three interpolation methods, Q-like checks, variable-μ identities, Hele–Shaw shape factors, and a manufactured energy balance. This is **not** a run of the production Python scripts or of 2WCF-SVD on real X-ray data. No prototype files were imported to the repository.

## 7. What not to infer

- Do not call this repository end-to-end reproducible merely because published methods and code exist: experimental images/reference scans, calibration fits, run configuration and PKLs live outside the repo.
- Do not transfer Natalia Shevchenko's calibration slope to the current test sequence: student Kristofers' independent slope is intentional and experiment-specific.
- Do not equate mass-fraction `w`, volume-fraction `φ`, and mole-fraction `x`.
- Do not infer flow compressibility from the difference between `||grad u||²` and `|curl u|²` without boundary and model terms.
- Do not expect `dK/dt + D = 0` over a cropped buoyancy-driven field.
