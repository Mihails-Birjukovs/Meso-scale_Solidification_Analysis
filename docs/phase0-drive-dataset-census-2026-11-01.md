# Phase 0 — extended Google Drive dataset census and archived postprocessing audit

**Date:** 2026-11-01 (Europe/Riga)  
**Status:** Read-only dataset admission audit following approved and merged PR #4 (`main` commit `80f9b28b59a6e15711e7f9c77723b6917121bce3`). No source code or reference experiment data was modified. All numbers below are direct archive observations or arithmetic checks, not claims of validated Ga–In mechanical-energy closure.

## 1. Settled conventions

Owner reconfirmed two decisions:
1. **Preserve image x-right / y-down** inside the present velocity reconstruction and interpolation; explicitly convert to physical Cartesian coordinates (y-up and physical +z curl) for physical integrals. Do not silently mix image and Cartesian derivatives.
2. Treat **OFV image-pair times and quantitative concentration alignment as a separate implementation**. Never infer acquisition FPS, raw binning or source indices from processed-archive titles or AVI playback settings.

These decisions remain authoritative for Phase 0 and later work.

## 2. Archive census and direct image inspection

The linked [2WCF-SVD Article / Image_sequences / Solidification](https://drive.google.com/drive/folders/1CHVHJiz8jiAXjUvB6Kw5Sz2AiMZm5Cpi) folder contains these **different** processed sequences:

| Image archive label | Frames | Frame shape (rows×columns) | Stored samples | Status |
|---|---:|---:|---|---|
| `20260331_...KLD_v2_Run1.7z` | 80 | 82×98 | 16-bit TIFF | Already fully tested against matching archived original 2WCF output |
| `20260527_...filtered_enhanced_v2_Run2.7z` | 100 | 68×170 | 16-bit TIFF | Archive and representative actual frame data inspected |
| `20260428_...filtered_enhanced_v2_Run2.7z` | 400 | 141×190 | 16-bit TIFF | Archive and representative actual frame data inspected |

Three further image archives are available under [Image_sequences](https://drive.google.com/drive/folders/1yP5XtRkbiq2SqR3qei45MbAFY8yb7G6R):

| Archive label | Frames | Shape | Direct check |
|---|---:|---:|---|
| `optical_density.7z` | 301 | 106×69 | 16-bit TIFF; several actual frames read |
| `optical_density_3D_filtered_TV_Gaussian_consRel_0.05.7z` | 301 | 106×69 | 16-bit TIFF; several actual frames read |
| `optical_density_3D_filtered_TV_Laplacian_consRel_1.15.7z` | 301 | 106×69 | 16-bit TIFF; several actual frames read |

The three 301-frame variants have the same frame numbering and image dimensions; this makes them useful **candidates** for a controlled filtering benchmark. They should not be called quantitatively calibrated optical-density measurements without a documented encoding, acquisition identity and reference model. Simple framewise image correlations between the two filtered versions were ~0.99 in representative later frames, but much lower early in the sequence; this establishes only related image content, **not** identical radiometry or physical transport. In particular these 301-frame images cannot simply be paired with the 80-frame 82×98 OFV series.

All archive contents were inventoried read-only with a local libarchive-backed 7z reader. Raw TIFFs and archives were not copied into GitHub.

## 3. Larger MSc raw archives: known metadata and access limitation

Owner-linked folder: [Kristofers MSc — Raw Images for MSc](https://drive.google.com/drive/folders/1So6iAgNoLnmcELurrMFBTpYVvWVldLjP).

| Drive file | Compressed bytes | Approx. GiB | Contents inspected? |
|---|---:|---:|---|
| `2011-09-09.7z` | 2,846,280,956 | 2.65 | No |
| `2014-04-04.7z` | 1,507,471,570 | 1.40 | No |
| `2014-04-15-Exp2.7z` | 1,181,517,718 | 1.10 | No |

**Verified limit:** Attempting to fetch the smallest (`2014-04-15-Exp2.7z`, Drive ID `1QvtoTxusV_mx1fJLGP4igomTiBm5ZNaw`) returned HTTP 413: `1181517718 bytes exceeds the 268435456-byte limit`. Accordingly **no claim is made about any archive's internal TIFFs, reference scans, frame timing, chamber walls or actual experiment date**. The names `2011` / `2014` are treated only as provided archive labels, not as demonstrated correspondence to the 2026-processed sets.

For efficient further verification, obtain a **small read-only exported subset** (example raw image, corresponding reference, camera/acquisition metadata and archive directory listing) or access the originals through an environment supporting larger-file reading. Do not split files merely to work around an unknown acquisition identity; first select a target experiment using source metadata.

## 4. New relevant archived downstream data: Kristofers PhD, 27 October

An additional [Kristofers PhD Drive folder](https://drive.google.com/drive/folders/1EaxfxxTnOqI_ukscr4Tfd3FqbsHH5FOP) contains `20261027.zip` (Drive ID `18tenFDxezfjSyySArEe5GxfYmViH-FLW`) and `20261027Nr2.zip` (ID `15CuSfM3cZPFHM6OGR-mxg3z9_okHECyj`), each ~34.5 MB.

**Observed archive structure (both):** 20 output frames, each with eight `30×50` NumPy arrays (`density`, `dissipation`, `enstrophy_field`, `gallium_fraction`, `kinetic_energy`, `speed`, `viscosity`, `vorticity`); `summary.csv`, `kinetic_energy_balance.csv`, and 209 PNG diagnostics/plots. No `Conc_In` TIFFs, 2WCF PKLs, original image/camera timestamps or exact source-code commit manifests were included in these two ZIPs. The `30×50` output grid is **geometrically compatible** with the 90×150 `gFiltered` image grid at a 3-pixel sample spacing, but this is **not proof** that the archives represent the same acquisition, nor justification to use `gFiltered` as calibrated composition.

### Exact numerical self-consistency of saved arrays (20 frames, each ZIP)

- Every `kinetic_energy` array is exactly `0.5 × density × speed²` for the stored arrays (observed maximum absolute discrepancy zero in both ZIPs).
- Summing the stored `kinetic_energy` field and multiplying by `summary.csv`'s `dV` reproduces reported total `E_total` within floating-point rounding (~`1e-28` J).
- Summing the stored `dissipation` field times `dV` reproduces the reported `kinetic_energy_balance.csv` dissipation within floating-point rounding (~`2e-28` W).
- The saved `viscosity` field matches the script's **legacy linear mass-fraction** mixture model with a maximum difference ~`2.1e-10` Pa·s (roundoff). **This is not the agreed volume-linear or mole-log law**, and no change to the stored historical data is implied.
- The saved `density` fields correspond closely to the approved volume-additive specific-volume law. Mean absolute difference when recalculated directly from the *downsampled* saved gallium fraction is ~`0.019 kg/m³`, maximum ~`0.274 kg/m³`. Since density and mass fraction were separately resampled, this small difference is not by itself evidence of a physics or code error; document the resampling operator before interpreting it.

### Comparing the two 27 October output variants

The two ZIPs have **bitwise identical** density, gallium-fraction and viscosity arrays for all 20 frames. Their velocity-derived fields are different:

| Saved field | Normalized RMS difference (Nr2 vs first ZIP) | Fieldwise Pearson correlation |
|---|---:|---:|
| speed | 0.146 | 0.969 |
| kinetic_energy | 0.321 | 0.924 |
| vorticity | 0.804 | 0.594 |
| dissipation | 0.985 | 0.167 |
| `enstrophy_field` | 0.989 | 0.133 |

Normalized RMS difference here is `sqrt(mean((B-A)²))/sqrt(mean(A²))` over all 20×30×50 stored samples. The differences are **observed** and **not assigned a cause**: no pipeline configuration or code-hash manifest was included. Their identical material properties exclude density/viscosity changes as the sole explanation. These arrays make a valuable regression comparison target when the original acquisition/run configuration becomes available.

The two CSVs use an explicit *output* time column 0–19 s, but no independent source-acquisition metadata proves its correctness for the source images. Their `relative_residual` is not a valid physical-energy-closure quality score: the old postprocessor omits gap wall drag, gravitational potential, and crop boundary terms. The old `enstrophy_field` name also refers to squared velocity gradient, not true vorticity enstrophy. **Do not infer OFV invalidity, fluid compressibility or real energy nonclosure from the saved historical residuals.**

## 5. G0 admission decision and next best experiment

**G0 remains partial.** We have an original 2WCF source-level numerical replay of 64,731 vectors for the 80-frame March-31-labelled test case, confirmed coordinate signs, and now independent evidence that 20-frame downstream output data are arithmetically self-consistent and sensitive to velocity reconstruction choices. We **do not yet have a trustworthy same-acquisition bundle** of raw/reference/calibrated concentration, upstream flow PKL, frame timing, crop transform and physical wall coordinates.

Suggested priority:
1. **Target existing 20-frame 27 October result runs** for provenance recovery: identify the matching source `Conc_In` images, upstream PKLs and saved run configuration so the large differences in derivatives/dissipation can be understood.
2. If not available, select a full-FOV experiment from the raw MSc archives **only after** obtaining a small directory listing, a few reference frames and acquisition metadata. The connector's large-file limit should not be mistaken for a scientific inconsistency in the data.
3. Use the **301-frame matched optical-density variants** and 100/400-frame solidification TIFF stacks for an independent numerical/photometric OFV filter benchmark when ready, explicitly separate from quantitative mass/energy validation.
4. Implement timestamp-to-concentration midpoint registration as a **distinct, reviewable PR** with refusal on missing calibration, crop or time provenance. Preserve image x-right/y-down reconstruction and physical y-up integration.

This is a documentation and dataset-selection analysis. No numerical/physical production algorithm was modified.
