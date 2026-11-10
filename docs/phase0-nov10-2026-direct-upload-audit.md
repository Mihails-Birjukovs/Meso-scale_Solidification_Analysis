# Scientific review of November 10 preprocessing/velocimetry upload (2026-11-11)

**Reviewed direct commit:** [`297a0a48d56b`](https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis/commit/297a0a48d56bb595f0e0ef39b422d0b9690f393f), committed 2026-11-10 02:16:03 UTC, parent `cc5120223777ce675ee2ee1c62a6c9b2f779e8e6`. The GitHub commit is titled **“Add files via upload”**, modifies only two research Python scripts, with **735 added and 741 deleted lines** in the commit comparison. It is independent of the user's approved #7/#8 PRs, both merged **after** the upload; no later changes by this audit overwrite those two production scripts.

**Source files frozen for review:**

| File | Blob at original November 10 commit | Review role |
|---|---|---|
| `Python_code/ImagePreprocessWithReference.py` | `a21b3ad720f3c35544e103a87df802875a2b124d` | image/reference correction, manual optical-density concentration calibration |
| `Python_code/VelocimetryRaksturlielumi.py` | `983a217d957cea9cc1cb907193d3f115b6a8fda0` | OFV interpolation, physical metrics and incomplete kinetic-energy balance |
| `Python_code/ofv_coordinate_conventions.py` | `8217b73200faeffb4bea45ab3096714a6bd33330` (unchanged in `main`) | agreed/tested conventions from [PR #3](https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis/pull/3) |

**Validation level:** direct GitHub source comparison plus reviewed current tests/CI and a limited exact-source X: 2014-03-07 admission probe. **The full November 10 interactive scripts were not executed** on an authenticated matching OFV+composition dataset; physical results must not be certified on code inspection alone. The direct upload itself has no confirmed dedicated GitHub Actions run. Passing tests from PRs #7/#8 do not cover the two modified application scripts.

## 1. Material improvements in `ImagePreprocessWithReference.py`

1. Explicit source/reference spatial shape equality and crop-bound checks (around lines 72–74, 150–163), reducing the risk of silent wrong-dimensional processing.
2. Strict positive/finite reference-only intensity admission with NaN markers for invalid pixels (around lines 240–283), and a refusal if downsampled normalized intensities remain nonfinite/nonpositive (around lines 375–380). **No negative optical density was secretly clipped to zero** in the displayed main quantitative path: `g=-ln(I/R)` is evaluated only for positive admitted ratios. These safeguards are useful, though physical radiometric fidelity still needs external reference validation.
3. Changes the spatial downsampling kernel from `cv2.INTER_LANCZOS4` to `cv2.INTER_AREA` (line ~369): this is a scientifically consequential filter change, appropriate to test with exact-source image benchmarks rather than call universally equivalent.
4. Adds a full-frame optical-density viewer and interactive P1/P2/P3 ROI acquisition, recording `g_mean,g_median,g_std,frame_index,coordinates`; assigns `C_In` with **measured vs assumed** provenance, computes a three-point least-squares `C_In=a*g+b`, saves calibration points and float32 concentration frames, and records a provisional metadata status. This is a useful advance over the previous fixed `270.1341*g+29.2945` conversion **provided the references are correctly attributed to the same experiment and phase**.
5. Applies median plus TV filtering to g and writes both unfiltered and filtered provisional concentration sets. Prints and records out-of-[0,100] concentration excursions without silently clipping them. **But these are not accepted physical liquid compositions without validated material masks, anchors, uncertainty and reference radiometry.**

## 2. Confirmed code regressions in `VelocimetryRaksturlielumi.py`

### P0: 2WCF inversion and image/Cartesian basis regression — [Issue #9](https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis/issues/9)

The 2026-11-10 version removes `require_inversion` and `forward_image_components` (`params.json` still read at lines 104–106, but `VelocityInversion` ignored). At lines 258–267 it converts saved u/v directly with `delta_x/delta_t`; at lines 365–377 it **flips just the vertical component** while still retaining an x-right/y-down grid. These operations explicitly regress [the reviewed PR #3 convention](https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis/pull/3), which requires undoing *both* upstream serialized-component factors, then keeping both components in image-forward coordinates during interpolation.

For `u_saved=s*u_image`, `v_saved=s*v_image` with upstream factor `s`, the new interpolated field is `U=s*f*u_image`, `V=-s*f*v_image`. Its naive curl `dV/dx-dU/dy=-s*f*(dv_image/dx+du_image/dy)` is **not** the physical +z curl `f*(du_image/dy-dv_image/dx)` in general. For manufactured image-forward `u=-y, v=x`, the required physical curl is `-2f`, whereas the new curl is **zero** for either nonzero s. For `u=x, v=-y`, originally divergence-free, the transformed field has generally nonzero divergence. This is stronger than a simple sign ambiguity and affects physically interpreted vectors, DFI, vorticity and divergence.

**Acceptance:** restore and test both-component inversion and one coherent grid basis; use the existing helper and manufactured-sign tests; require upstream PKL/parameters source hash. No hotfix applied here.

### P0: Unreviewed method switch from divergence-free RBF to linear interpolation — [Issue #10](https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis/issues/10)

At lines 471–482, production `U,V` switch from `U_rbf,V_rbf` to **`U_linear,V_linear`**, while the adjacent comment still says RBF is the selected main method. `scipy.interpolate.griddata(...,method="linear")` returns nonfinite values outside the convex hull unless support is explicitly handled. Although a linear-coverage mask is computed, the new selected `U,V` propagate without requiring finite physical integration domain through gradients, vorticity, dissipation, energy and numerical volume integrals (lines 557–670). Separately, RBF hold-out error is still reported for the RBF, **not for the selected downstream linear field**.

**Acceptance:** explicitly version which interpolation is production and require field finite/support masks and matched-domain statistics; enforce synthetic sparse-field and real-source numerical tests. Do not present `dK/dt+D` as full Hele–Shaw mechanical energy closure (wall drag, gravity, boundary flux and variable-density transport remain untreated).

## 3. Physical-admission gaps (partly pre-existing) — [Issue #11](https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis/issues/11)

- Preprocessor still hardcodes `dt0=0.2 s`, `bin_size=5`, `dx0=17.5 µm/px` (lines 343–354 and 383–385). Postprocessor still assumes `frame_rate=5,bin_factor=5`, `delta_x=17.5e-6*4` (lines 78–82). Original filename-interval evidence and v25 notebook metadata are **dataset-specific**; these constants must not be exported to 2014-03-07 (v25 lists 37.6 µm/px) without an independently validated source map.
- The postprocessor's selected PKL folder is labelled **20260915PKL**, and concentration folder is now labelled **20261110**. This is **not proof** of mixed acquisitions but likewise **not proof of shared sources**. File ordinal pairing at lines 120–140, `n_frames=min(...)`, does not apply the separately merged `phase0_time_registration.py` pair-center manifest contract and does not prove matching crop and physical reference.
- The full-frame manual calibration ROI viewer (lines 477–675) uses a **validity-weighted** full-image binning rule, while the exported cropped g fields use a different strict finite-domain mean/downsample path (lines 240–389), with potentially different temporal `start_frame` and crop offsets. Without a source/ROI coordinate map, anchor values can be attributed to the wrong frame or spatial region.
- The new linear three-point calibration is provisional and applies even to solids, walls and unknown invalid detector regions without a **verified physical liquid-domain mask**; the recorded outside-[0,100] rate and `calibration_status="provisional_assumed_points"` are warnings, not acceptance. No comparison of reconstructed mean reference/dark vs no-dark branches is implemented for experiments with actual dark sequences.
- Mixture density from `1/(w_Ga/rho_Ga+w_In/rho_In)` is preserved (correct interpretation for indium/gallium **mass fractions** under additive specific volumes). The mass-weighted linear viscosity relation is a model assumption, not established physically correct by the preceding mixture-density fix. `enstrophy_field` names the squared velocity-gradient norm, not `omega^2`: record semantic distinctions rather than infer a new regression.
- No complete experimental kinetic/momentum conservation or uncertainty propagation claimed or demonstrated. Separate G3/G4 gates apply after admission G0.

## 4. User-approved extension: 2014-03-07 — [Issue #12](https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis/issues/12)

The *actual user-supplied private X:* archived case has **500** contiguous `Frame_1..500.tiff` processed 16-bit cropped images (567×276), and **418** `Frame_1..418.png` saved historical binary solid masks (763×384). The `Selected Frame IDs.csv` contains exactly **418** source IDs `600,605,...,2685`. Exact import in local Mathematica verified sampled source TIFFs are ImageType `Bit16` with original TIFF `Compression=32946` (old-style Deflate), and saved masks have 1-bit grayscale PNG data with actual values 0/255. Their **different geometries and unproven source/crop transform** forbid direct per-pixel Dice or treating the saved masks as independent manual truth. Other 82 saved cropped frames have no companion masks in this set. The v25 notebook documents **37.6 µm/pixel** and **1-second exposure** for 2014-03-07, neither independently certifying the timestamp or intermediate resizing.

This branch introduces a **machine-readable case registry**, dependency-free **read-only inventory/geometry/header/SHA admission tool** and synthetic refusal tests for 2014-03-07, with an executed actual X: manifest. This adds the case to the empirical MIL solid / masked-liquid K-medoids **test matrix** while refusing experimental `C_{In}(P)` acceptance until all `P` anchors and physical crop/camera/radiometry provenance are established. Distinguish semantic roles of high-In solid dendrites, Ga-rich liquid channels and bulk/plume regions: a nine/more-level K-medoids intensity cluster **is not itself a chemical composition anchor**.

### 2014-03-07 X: audit output

Private workspace `X:\AI-Lab-Test\Solidification_OFV\analysis_outputs\phase0_2014-03-07_admission_2026-11-11` holds:
- `2014-03-07_full_source_inventory.json` — hashes of **all 500 TIFFs and 418 masks**, exact dimensions/IDs, raw archive owner-provided path relative to the analysis. **SHA256 `63dc854162b5d928d187689e1e34e983b0774c915b43eb7e8fdd216dcb370338`**, 151335 bytes.
- The exact source files from this proposed branch, downloaded and verified **Git blob SHA** before executing: `phase0_2014_03_07_case_admission.py` blob `46cd887d7af9d0045b9a7377857a219856aeed8d` and case JSON blob `255635ab9565b683d783903020826ad57a43e687`.
- `2014_03_07_image_mask_import.wls` and parsed sample metadata, independently inspected with the local Wolfram kernel; actual pixel decoding was done by Mathematica, whereas the public admission tool explicitly parses TIFF/PNG **headers only**.

## 5. Acceptance and non-claims

| Gate | As of this audit |
|---|---|
| PR #7 and PR #8 owner approval and merge into current `main` | **PASS** — merges `e6ebc9842fdda491ec768472399a32fcf0dd6991`, `205d0933d7330ebbba40d6afd52d29117b37eeef` |
| November 10 source diff, input/sign/interpolation semantics | **PASS static inspection** |
| Source-unified OFV velocity physical direction + vorticity | **FAIL static regression**, Issue #9 |
| RBF-vs-linear selection and full-domain finite aggregates | **FAIL unguarded algorithm selection**, Issue #10 |
| Exact matched experimental flow/calibration/clock/geometry | **BLOCKED**, Issue #11 |
| 2014-03-07 500/418 source inventory, header geometry/hash | **PASS for provenance**, Issue #12 |
| 2014-03-07 image-to-mask spatial/coregistration and physical labels | **BLOCKED**, Issue #12 |
| 2014-03-07 automated `C_{In}(P)` physical calibration, held-out accuracy | **NOT RUN / BLOCKED** |
| Scientific original X: / notebook changes | **NONE** |

**This is a docs/test/admission PR, not a silent scientific code fix.** The direct November 10 upload has not been reverted; any remediation should be a separate reviewed PR with source-matched numerical benchmarks and the user’s explicit approval.
