# Phase 0 — Representative radiograph and coordinate-sign evaluation (2026-11-01)

**Status:** Source-matched independent diagnostic plus a focused follow-on code correction, **not a full upstream execution**. The revised postprocessor has not yet been exercised with a calibrated experimental Ga–In concentration/PKL pair. G0 remains open.

## Source and data identities

- Target source baseline: `Mihails-Birjukovs/Meso-scale_Solidification_Analysis`, `main` after approved PR #2, merge commit `a955512a00befd5b951eae22e38782917c154a20`.
- Optical-flow upstream: `pienins/Optical-flow-svd-and-fourier-filtering` at commit `27659ae0e0f798189e1fc7c4516453374ad3c9eb`, file `2WCF-SVD_v4_4.py` blob `52d20820314a1e4283a325dc34e899191bf267b4`.
- Representative input: `20260331_4 Downsampled ImagesRun1_20260331_v3_3D_filtered_enhanced_KLD_v2_Run1.7z`, Google Drive file ID `1tnxbxv2BI5F0RDWF0oF3mBI7YPfsq3l-`; previously obtained as authorized user content. Do not publish this archive without explicit data rights.
- Internal archive: 80 ordered 16-bit TIFF files `Frame_1.tiff` through `Frame_80.tiff`, shape **82 rows x 98 columns**. First-frame SHA-256: `0f4085dad0585cd4f8e196211f294a00e8375c31a981c61c3f5cc6cc6b86862b`.
- Preflight: unambiguously sorted by trailing positive integer 1–80, then staged without re-encoding as `filtered3D_00000.tiff` through `filtered3D_00079.tiff`; SHA-256 equality tested between source and staged files.

## Execution/evidence boundary

An independent local Python diagnostic **reproduced the inspected 2WCF pair algorithm settings**, using locally installed OpenCV 4.13.0, NumPy, SciPy and TIFF reading; it was **not imported from or run through** the pinned upstream 2WCF source, since an executable pinned checkout was not available locally and `wolframclient` was absent. Do NOT label this numerical exercise a byte-for-byte reproduction of the upstream application. In particular, output PKLs, WXF files, the upstream AVI and parameter snapshot were **not** produced by this diagnostic; Phase-0 integration G0 remains unpassed.

The diagnostic uses per-frame min/max uint8 normalization, cv2 Farnebäck with (pyr_scale .75, levels 8, window 25, iterations 10, poly_n 7, sigma 2, flags 0), forward/backward warping and consistency, scaled MAD, confidence exp[-(error/sigma_frame)^2], 5x5 box-weighted smoothing, 7-pixel sampling offset by 3, MinConfidence .01.

## Observed metrics on real filtered image content

| Statistic | Value | Interpretation |
|---|---:|---|
| Image frames / image pairs | 80 / 79 | 1 velocity result per adjacent image pair |
| Nominal sample grid | 12 rows x 14 columns | 168 possible arrows per pair |
| Median accepted fraction | 0.9643 | 96.43% of nominal sample vectors, not physical accuracy |
| Worst accepted fraction | 0.5714 | Some image pairs are much less reliable |
| Median apparent speed | 0.7179 pixel/image pair | Not m/s without verified frame timing and pixel scale |
| 95th percentile of pairwise median speeds | 2.7595 pixel/image pair | Temporal variability |
| Median forward/backward error | 0.1140 pixel | Internal algorithm consistency, not an independent ground truth |
| Image mean intensity span | 87.24% of average mean | Significant photometric variation; may reflect actual transport and/or acquisition effects |

No inference of true barycentric velocity, gravity-driven flow orientation, spatial domain walls, or energy-budget closure follows from these numbers.

## Ground-truth direction tests constructed from the actual first frame

A known translation of the first real image was generated with OpenCV warpAffine/border reflect; inferred median **forward image-coordinate** displacements were:

| Injected shift (px; x right, y down) | Median recovered u (px) | Median recovered v (px) |
|---|---:|---:|
| (+1, 0) | +0.95450 | +0.00030 |
| (-1, 0) | -0.95447 | -0.00004 |
| (0, +1) | -0.01061 | +0.89677 |
| (0, -1) | +0.00140 | -0.95772 |
| (+1, +1) | +0.94756 | +0.89668 |
| (-1, -1) | -0.95432 | -0.95967 |
| (+2, -1) | +1.93515 | -0.96744 |

These confirm the sign convention of the source-matched Farnebäck computation, not exact subpixel-unbiased recovery. Source 2WCF `VelocityInversion=-1` multiplies **both** these components before saving, which we confirmed by direct upstream source inspection.

For physical Cartesian axes x-right/y-UP:
- `u_phys = u_saved / inversion * (pixel_size / frame_pair_dt)`;
- `v_phys = -v_saved / inversion * (pixel_size / frame_pair_dt)`.

For the existing postprocessor's **unchanged image-coordinate grid**, the correct internal input is instead `u_image=u_saved/inversion`, `v_image=v_saved/inversion` (both multiplied by pixel_size/frame_dt). It is inconsistent to flip only v while leaving positions in image coordinates.

The physical out-of-plane vorticity of an image-grid reconstruction is `omega_phys = du_image/dy_image - dv_image/dx_image`, the **negative** of the naive image-coordinate curl. Divergence and Newtonian scalar strain dissipation are invariant under this coordinated reflection.


## Archived original 2WCF output — subsequently recovered on 2026-11-01

A *separate matching-by-filename* run archive was recovered from the user's connected Drive:
`20260331_4 Downsampled ImagesRun1_20260331_v3_3D_filtered_enhanced_KLD_v2_Run1_run_2.7z`, Drive file ID `1A7fBi_jZDlzHCoZvJAjPXFP3O0ngusjn`.

This archive contains exactly **79 PKL** vector files indexed `velocity_field_00000.pkl` through `velocity_field_00078.pkl`, **79 WXF** files, a 79-row `flow_qc_metrics.csv`, `parameters.json`, CSV parameters, a plot, and AVI output. The PKLs were inspected with an explicitly restricted allowlist for NumPy pickled-array constructors; no arbitrary pickle code was permitted. All 79 vector records contain finite one-dimensional arrays `x,y,u,v`, consistent lengths, and samples on the expected **ArrowDensityStep=3** grid, x/y indices starting at 1. The 82×98 shape permits 27×33 = 891 nominal sample points. Observed counts range **576–891**, median **852**.

**Actual archived parameters:** `VelocityInversion=-1`, `ArrowDensityStep=3`, `USE_SVD=true`, `KillIDs=[0]`, `UseConfidenceSmoothing=true`, `ConfidenceSigma=5`, `ConfidenceKernelSize=5`, `MinConfidence=0.01`, Farnebäck settings 0.75/8/25/10/7/2, `MedianOfMeansGroupSize=1000`, `VideoFPS=5`. The metadata do **not** include a source-code commit hash or acquisition timing manifest. VideoFPS is a visualization setting, **not proof of source acquisition FPS**.

| Actual archived output statistic | Value |
|---|---:|
| Original PKL / WXF / QC records | 79 / 79 / 79 |
| Original median vectors per pair | 852 |
| Original median apparent speed over pairs | 0.8912 px/pair |
| Original median forward-backward error over pairs | 0.1191 px |
| Median pairwise u-forward (undoing inversion) | +0.0577 px/pair |
| Median pairwise v-forward (image y-down) | -0.3664 px/pair |

The archived output uses *SVD filtering and 3-pixel sparse sampling*, unlike the earlier source-matched diagnostic (which did not apply SVD and used 7-pixel sampling). The two computations must **not** be treated as an exact numerical reproduction or a quantitative algorithm-regression comparison.

This establishes the original **saved-data interface** against real archived outputs and supports the coordinate convention documented above. However, it **does not establish the exact upstream generating commit**, measured time axis, physical flow direction, quantitative concentration field registration, or any energy budget. The original upstream program was **not re-executed** in the current runtime.

## Focused coordinate-sign correction on this feature branch

The proposed follow-on PR:
- Adds a pure small conversion helper requiring an explicit upstream `VelocityInversion`; no default is guessed.
- Changes only conversion of both raw saved vector components to image-forward velocities in `VelocimetryRaksturlielumi.py`.
- Removes the later lone `v` flip, making production and RBF hold-out use the **same** sign convention.
- Sets the plotted/recorded physical +z vorticity sign correctly for internal image y-down orientation.
- Adds focused synthetic regression tests; does **not** change density C03, Kristofers calibration, concentration preprocessing, interpolation choice, frame midpoint registration, or the external upstream.

## Still required to complete G0

1. Run the original pinned 2WCF program in an isolated environment and verify its actual outputs/parameters and position-sampling grid on this sequence.
2. Match the TIFF sequence to its original experiment/source frame index, crop, acquisition fps, physical image pitch and `Conc_In` output from the **same acquisition**. The processed archive title alone does not establish these.
3. Verify actual PKL vector orientation/physical velocities on synthetic known motion through the complete original I/O path; compare with source-matched diagnostics above.
4. Record material/radiometric calibration provenance and full-cell wall coordinates before higher-order physics.
5. Benchmark updated postprocessor on real paired flow vectors and composition fields before claiming physical vorticity or energy validity.

**Note on rights:** Do not commit raw images or a copied upstream 2WCF implementation to this public repository without data/redistribution permission. This report includes only compact aggregate diagnostics and synthetic-transformation summary results.
