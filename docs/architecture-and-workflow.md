# Architecture, data flow and operating contract

**Status:** Current-code interfaces followed by proposed integration contracts. The external 2WCF-SVD repository is a read-only dependency.

## 1. Software responsibility map

```text
Raw 16-bit X-ray radiographs + beam/reference + acquisition metadata
  |
  +--> established solidification branch [Mathematica]
  |       Dendrite & Plume Analysis v25.nb
  |       -> solid/liquid segmentation, cavities/chimneys,
  |          front motion, skeleton/orientation/grains, plumes
  |
  +--> Python_code/ImagePreprocessWithReference.py
          |  crop, reference correction, temporal binning, spatial resampling
          |
          +--> quantitative radiometry
          |    optical density -> Kristofers' calibrated In wt.%
          |    -> mass fraction, later density/viscosity
          |    NO histogram-matching deflicker for quantitative data
          |
          +--> motion-estimation images
               current: strong enhancement + spatiotemporal TV
               PLANNED options: minimal / TV / TV + histogram deflicker
               -> .tiff sequence with explicit provenance manifest
                      |
                      v
             2WCF-SVD_v4_4.py [OTHER repository, READ-ONLY]
             -> velocity_field_00000.pkl (x,y,u,v)
             -> parameters.json; flow_qc_metrics.csv
                      |
                      v
             VelocimetryRaksturlielumi.py
             + calibrated concentration fields, frame IDs/times,
               reference coordinates and masks
             -> reconstructed velocity + confidence/coverage
             -> strain, vorticity, Q-like quantity, divergence
             -> rho(w), mu(w), K, dissipation, continuity/energy diagnostics
```

## 2. Current artifact lineage

| Artifact | Scientific role | Development disposition |
|---|---|---|
| `Mathematica_code/Dendrite & Plume Analysis v25.nb` | Source for peer-reviewed segmentation, fronts, liquid plumes and dendritic morphology | Retain; potential aligned mask export later |
| `Mathematica_code/Optical Flow -- Image Filtering.nb` | Historical prototype filtering / KLD/SVD method | Reference for Python velocity-input preprocessing |
| `Mathematica_code/OFV_field_postprocessing_v2.nb` | Historical WXF flow visualization and diagnostic checks | Mostly superseded, read-only reference |
| `Python_code/ImagePreprocessWithReference.py` | Active image sequence preparation for optical flow, with quantitative side outputs | Main revision target |
| `Python_code/VelocimetryRaksturlielumi.py` | Active flow-field characterization and physics | Main revision target |

## 3. Verified current external I/O

The external [2WCF-SVD v4.4 source](https://github.com/pienins/Optical-flow-svd-and-fourier-filtering/blob/main/2WCF-SVD_v4_4.py) uses `*.tiff` in its TIFF loader, numeric filename sorting, per-frame uint8 normalization, optional temporal SVD, forward/backward OpenCV Farnebäck flow and confidence/error filtering. It computes flow **between frame i and i+1**, then exports:
- `pkl/velocity_field_%05d.pkl`, a pickle containing arrays `x, y, u, v` measured at sparse pixel-grid points.
- Parallel WXF files, a `parameters.json` and `flow_qc_metrics.csv`.
- `ArrowDensityStep` and `VelocityInversion` are in the parameter JSON. The inspected script defaults to `VelocityInversion=-1` and multiplies **both** vector components by it *before* output.

**Present mismatch:** local preprocessing exports `filtered3D_%05d.tif`, not `*.tiff`. This must be corrected on this project's output side; do **not** edit external 2WCF-SVD.

**Timestamp contract (proposed):** each preprocessed frame has a source-frame ID, bin start/end, effective center time and crop geometry; velocity pair i is assigned `t_OFV,i=(t_img,i+t_img,i+1)/2`. The concentration corresponding to that velocity is interpolated from the two aligned concentration frames or otherwise assigned with a documented consistent temporal rule.

## 4. Coordinates and units

Image coordinates: `x` right, `y_img` downward, pixel origin at top-left. Physical coordinates: `x_phys` right, `y_phys` **upward**, `z` across gap. For image height `H`, pixel spacing `s`, and an appropriate reference:
```text
x_phys = s*x_pix
y_phys = s*(H-1-y_img)
u_phys = +s*u_img / dt
v_phys = -s*v_img / dt
```
**Provided that** `u_img,v_img` are actual forward displacements from the earlier to the later image. The upstream `VelocityInversion` changes that meaning; undo or otherwise explicitly account for it first. Always transform coordinate positions and vector components together. Use physical `dx,dy` when differentiating velocity fields and document which axis order `np.gradient` expects.

Working values in scripts: nominal source pixel pitch `17.5 µm/px`, spatial downsampling factor `4`, effective pixel pitch `70 µm/px`; source 5 fps, temporal nonoverlapping mean bins of 5, nominal `dt_eff=1 s`; gap thickness `0.15 mm`. These are **dataset-specific working values**, not universal properties.

## 5. Quantitative concentration and the OFV branch are separate

The indium calibration for the current test images was independently derived by Kristofers Rolands Kangīzers: `C_In(wt.%) = 270.1341*g + 29.2945` for the signal and reference protocol in the current image set. This is **not** Natalia Shevchenko's separate calibration, `156.7*P+27.0`, from different experimental X-ray conditions. Do not substitute one fit into the other's dataset.

For concentration, use radiometrically traceable dark/reference correction and the documented calibration. Filtering chosen solely to improve optical-flow contrast (histogram matching, strong nonlinear enhancement) is not automatically quantitative and must **not** feed back into concentration reconstruction.

## 6. Proposed run manifest

Store a machine-readable manifest **alongside outputs**, not necessarily with experimental data in GitHub:

```json
{
  "experiment_id": "dataset-specific-ID",
  "source_images": {"folder": "...", "frame_ids": [100, 101], "fps": 5.0},
  "radiometry": {"reference_kind": "initial_melt_or_beam", "dark_correction": false},
  "geometry": {"gap_m": 0.00015, "pixel_pitch_m": 0.0000175, "crop_xywh_pixels": [0, 0, 100, 100]},
  "preprocess": {"spatial_downsample": 4, "time_bin": 5, "mode": "tv_plus_deflicker"},
  "calibration": {"composition_basis": "indium_mass_percent", "fit_id": "Kristofers-current-experiment"},
  "ofv": {"upstream_commit": "record-sha", "image_pair_index": 0, "velocity_inversion": -1},
  "analysis": {"coordinates": "x-right-y-up", "interpolation": "unconstrained_rbf"},
  "validations": {"mask_id": "same-domain", "holdout_seed": 42}
}
```

This is an **illustrative desired schema**; the current code does not output it in full. The manifest should additionally store true source-file hashes, calibration fit uncertainty, temporal centering, crop transforms, and image/fitted-vector sizes.

## 7. Safety, reproducibility and data ownership

- Loading untrusted Python PKLs is unsafe. Restrict the analysis to trusted experimental outputs or convert vectors to a safer interchange format.
- Raw experiments and collaborator communications are not embedded or publicly redistributed by this documentation.
- GitHub repository MIT license does not automatically license experimental images or third-party BM3D/MATLink code.
- Prefer synthetic tests and short, traceable test fixtures before refactoring the active scripts.
