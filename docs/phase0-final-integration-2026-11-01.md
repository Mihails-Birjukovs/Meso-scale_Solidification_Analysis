# Phase 0 — final integration preflight, 1 November 2026

**Result: G0 PARTIAL / not yet accepted for experimental Ga–In physical inference.** After merging approved [PR #3](https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis/pull/3) (merge SHA `5dba5253e17774f6e4091867607f5ae58f618931`), we verified the original input/OFV interface and all archived vector records. The remaining blockers are **same-acquisition calibrated concentration**, true acquisition timestamps, and physical image/crop reference. This document does not assert that those inputs exist or that the full postprocessor has passed.

## Immutable evidence identities

- Target: `Mihails-Birjukovs/Meso-scale_Solidification_Analysis@5dba5253e17774f6e4091867607f5ae58f618931` (accepted PR #3). Approved source fix retains an image x-right/y-down interpolation grid, undoes both saved upstream velocity inversions, and uses the Cartesian physical vorticity sign.
- Original source: `pienins/Optical-flow-svd-and-fourier-filtering@27659ae0e0f798189e1fc7c4516453374ad3c9eb`, `2WCF-SVD_v4_4.py`, Git blob `52d20820314a1e4283a325dc34e899191bf267b4`; it was previously executed with an import shim only for the unused optional WXF writer. Its numerical core matched all archived vectors.
- Input archive: `20260331_4 Downsampled ImagesRun1_20260331_v3_3D_filtered_enhanced_KLD_v2_Run1.7z`; Drive ID `1tnxbxv2BI5F0RDWF0oF3mBI7YPfsq3l-`; SHA-256 `2d4f96e36d1230b3659c8f74d64754dc90f57e3354f1728bfb5c5c9ac1a0e495`.
- Original output archive: same name with suffix `_run_2.7z`; Drive ID `1A7fBi_jZDlzHCoZvJAjPXFP3O0ngusjn`; SHA-256 `4dba02dc98f49dbe6dde315b9fefe707514e659a0781c732a55ad84899f5f2c8`.
- Run parameters obtained from historical `parameters.json`: `ArrowDensityStep=3`, `VelocityInversion=-1`, `USE_SVD=true`, `KillIDs=[0]`, confidence smoothing enabled. **`VideoFPS=5` does not prove camera acquisition rate.**

## Tests actually performed

| Admission or consistency check | Observation | Decision |
|---|---|---|
| PR #3 integrated and prior offline CI | GitHub merge verified; 22 tests passed on PR head | PASS |
| Image TIFF sequence | 80 consecutively numbered frames `Frame_1`–`Frame_80`, 82 rows × 98 cols, uint16 | PASS |
| Flow pair files | 79 consecutively numbered `velocity_field_00000`–`00078.pkl`; QC 79 rows (and prior verification of 79 WXF files) | PASS |
| Actual PKL record schema | All 79 have finite 1D `x,y,u,v` of equal lengths | PASS |
| Sampling geometry | x/y sampled at 1 modulo 3 px; nominal grid 27×33 = 891; all sampled positions unique and inside image bounds | PASS |
| Vector coverage | 64,731 vectors total; per pair 576–891; median 852/891 = 95.62%; minimum fraction 64.65% | PASS — descriptive |
| Linear support in common 27×33 sampling grid | Median 100%; minimum 84.74% | PASS — descriptive only |
| Neighbor-supported gradient coverage | Median 100%; minimum 82.83% | PASS — descriptive only |
| Saved-vector to Cartesian sign convention | Reflected image x-right/y-down to physical x-right/y-up across all 79 records; both saved components divided by recorded inversion | PASS — algebraic |
| Exact original-core numerical replay (earlier check) | 79/79 flow pairs and 64,731/64,731 sample positions matched; median per-pair vector RMSE ≈1.519×10⁻⁷ px | PASS — numerical core |
| Quantitative `Conc_In` maps for the **same acquisition** | No suitable registered set found in reviewed Drive and active local evidence | BLOCKED |
| Candidate Drive `gFiltered` sequence | 80 float32 optical-density frames but 90×150 shape, versus 82×98 OFV images; no matching crop transform | **REJECT direct pairing** |
| Absolute time origin and raw-to-bin mapping | Source start ID, raw acquisition FPS and original exposure timestamps absent from this archive's provenance | BLOCKED |
| Physical global coordinates and walls | Original crop offsets, spatial origin, cell wall locations not established | BLOCKED |
| Experimental full postprocessor / mechanical energy closure | No same-experiment quantitative image, flow and geometry bundle | NOT RUN |

The Drive `gFiltered` files were found under `Kristofers_MSc/Python/gFiltred/20260825_Nr1`; `g_filtered_parameters.json` explicitly reports **90×150**, 80 frames, float32, a filtering sequence, and `dx_eff_um_per_pixel=70.0`. Three files (`00000`, `00001`, `00079`) were read and independently confirmed to have shape 90×150. They are not the required **unmodified quantitative concentration** branch and cannot safely be matched to 82×98 OFV images just because both have 80 frames. Their particular relationship to the chosen OFV archive is unverified rather than disproven.

## Sign, velocity and timing contracts

For optical flow computed by OpenCV as image-forward displacement (x right, image y **down**), the original 2WCF source saves `(u_saved,v_saved)=VelocityInversion*(u_forward,v_forward)`. For physical y **up**, the conversion at image-pair duration `dt` and effective pixel pitch `s` is

```text
u_phys =  (u_saved / VelocityInversion) * s/dt
v_phys = -(v_saved / VelocityInversion) * s/dt
```

The merged production script keeps x/y *positions* and both *flow components* in image coordinates for sparse interpolation, but derives physical +z vorticity from `ω_z=∂u_image/∂y_image−∂v_image/∂x_image`. Scalar divergence is reflection invariant, but physical potential-energy height needs a full-cell spatial reference.

For nonoverlapping B-frame bins of raw frame-center interval `dt0`, global raw start index `j0` and raw clock origin `t0`:

```text
T_bin,i = t0 + [j0 + i B + (B-1)/2] dt0
T_flow,i = (T_bin,i + T_bin,i+1)/2
```

These are **conditional model timestamps**, not measured acquisition metadata. Neither `VideoFPS` nor the archive processing date can replace verified camera timing.

## Decision and next input required

**G0 = partial.** All available original image ↔ actual 2WCF vector I/O and sign checks passed. No physical divergence, enstrophy, kinetic-energy or mass/energy balance should be interpreted yet. The postprocessor's current index-based `Conc_In` / PKL pairing and shape-only density `zoom` also remain unresolved, and must not be exercised on the mismatched Drive candidates.

For physical G0 closure, obtain **one coherent experiment-level bundle** identifying original frame numbers and exposure timestamps, reference images and Kristofers' correct acquisition-specific concentration calibration, calibrated quantitative `Conc_In_%05d.tif` fields (or raw/reference inputs to regenerate them), the crop offsets and physical walls, and the matching 2WCF flow outputs/parameters. Once these exist, audit the transforms, register each velocity **pair midpoint** to an appropriate concentration measurement, and do an actual full postprocessor smoke test. Until then reject unsafe physical assertions.

## Reproducibility and security

The local analysis produced `final_integration_audit.py`, `final_integration_pairs.csv`, `final_integration_summary.json` and two coverage plots. The script uses a restricted NumPy pickle-global allowlist; it still should only receive trusted research PKLs. It uses piecewise-linear interpolation **solely to describe coverage**, not as a replacement for production divergence-free RBF or a comparison of physical accuracy. Input/output archives, measured TIFFs, and third-party upstream source are **not** committed to GitHub. The user received a separate lightweight ZIP containing this source/CSV/plot evidence but not private/third-party data.

See also [the earlier representative run report](phase0-representative-sequence-2026-11-01.md), [Phase-0 OFV contract](phase0-ofv-integration.md), and [approved validation roadmap](validation-roadmap.md).
