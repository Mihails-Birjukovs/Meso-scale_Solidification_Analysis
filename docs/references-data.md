# Publications, dependencies, calibration provenance, and external datasets

**Documentation snapshot:** 2026-10-22. Historical research methods, current source and proposed modeling extensions have different evidence levels. Revisit article versions, licenses and experimental file metadata before a public research reproducibility release.

## 1. Primary publication

**Birjukovs, M.; Shevchenko, N.; Eckert, S.** (2023). *An image processing pipeline for in situ dynamic X-ray imaging of directional solidification of metal alloys in thin cells.* **Experiments in Fluids** 64, 131. https://doi.org/10.1007/s00348-023-03671-2

- Main article: https://link.springer.com/article/10.1007/s00348-023-03671-2
- Supplement: https://media.springernature.com/original/springer-static/esm/art%3A10.1007%2Fs00348-023-03671-2/MediaObjects/348_2023_3671_MOESM1_ESM.pdf
- The paper documents the established solidification image-analysis pipeline and provides segmentation and morphology examples. The supplement's Appendix A provides flat-field/dark-current correction equations; Appendices B–J provide specific filtering, skeleton/grain, segmentation and liquid-domain analysis settings. The **current composition-aware OFV postprocessing extension is not asserted to be part of this published 2023 implementation**.

## 2. Related Ga–In experimental publications

- **Shevchenko, N. et al. (2015)**. *The effect of natural and forced melt convection on dendritic solidification in Ga–In alloys.* **Journal of Crystal Growth** 417. https://doi.org/10.1016/j.jcrysgro.2014.11.043
- **Shevchenko, N.; Boden, S.; Gerbeth, G.; Eckert, S. (2013).** *Chimney Formation in Solidifying Ga–25 wt pct In Alloys.* **Metallurgical and Materials Transactions A**. https://doi.org/10.1007/s11661-013-1711-1
- **Kao, A. et al. (2020)**. *Magnetic Effects on Microstructure and Solute Plume Dynamics of Directionally Solidifying Ga–In Alloy.* **JOM**. https://doi.org/10.1007/s11837-020-04305-2 . Discusses concentration in X-ray imaging contexts, but is not authorization to reuse a numeric fit across experiments.
- **Plevachuk, Y.; Sklyarchuk, V.; Shevchenko, N.; Eckert, S. (2015)**. *Electrophysical and structure-sensitive properties of liquid Ga–In alloys.* DOI/publication details should be reverified before numerical property fits; earlier literature search indicated https://doi.org/10.3139/146.111151 .

**Material-property caution:** The current `rho_Ga=5904 kg/m³`, `rho_In=7310 kg/m³`, `mu_Ga=1.7e-3 Pa*s`, `mu_In=1.3e-3 Pa*s` appear as working parameters in the downstream Python script. These are **not established in this documentation as correct composition- or temperature-specific pure-liquid material-property tables**. In particular pure indium's melting temperature complicates taking room-temperature pure-liquid endpoints literally. Treat any selected mixture law as a sensitivity approximation pending property verification.

## 3. Experiment-specific radiographic composition calibration

**Current test images:** `C_In(wt.%)=270.1341*g+29.2945` was calibrated separately by Kristofers Rolands Kangīzers for this dataset. The owner explicitly confirmed its separate origin. Its source references, fitted parameter uncertainties and valid X-ray conditions should be recorded with experimental data. **Do not replace it with the fit below.**

**Different experiment / methodological comparison:** Natalia Shevchenko recovered a 2026-09-01 calibration-method note and Origin plot. Three approximate references: 25 wt.% initial alloy with `P=-ln(I/I0)=0`, 5–10 wt.% Ga-rich channel, ~98.6 wt.% In-rich dendrites; recovered three-point illustrative fit `C_In(wt.%)=156.7P+27.0` with `R²=0.9986`. She cautioned on 2026-09-03 about different X-ray conditions. The underlying correspondence and documents are held separately; **this public repository does not redistribute private communications or the calibration attachments**.

Important reference distinction: a calibration using an **initial-melt** reference intensity `I0` is not automatically interchangeable with a radiometric **beam/flat-field** normalization. Track the exact reference definition.

## 4. Software and algorithm links

| Link | Used for | Caveat |
|---|---|---|
| http://matlink.org/ , https://github.com/rsmenon/MATLink | Historical Mathematica-MATLAB bridge | Version compatibility with modern platforms requires fresh testing |
| https://webpages.tuni.fi/foi/GCF-BM3D/index.html#ref_software | MATLAB/Python BM3D denoising | Current distributions, versions, license not automatically covered by this repo's MIT |
| https://github.com/Peteris-Zvejnieks/DivergenceFreeInterpolation | External solenoidal RBF library used in current Python | Dense conditioning, near-singularity, compact-support coverage must be benchmarked |
| https://github.com/pienins/Optical-flow-svd-and-fourier-filtering | **Read-only upstream** 2WCF-SVD optical flow | Source v4.4 uses `*.tiff`, creates sparse PKLs, `parameters.json`, QC metrics; **do not edit** |
| https://mihails-birjukovs.github.io/OOC_Particles_Velocimetry_Docs/ | OOC PIV/PTV image-analysis documentation | `docs/reference/METHODS.md` documents reference-frame histogram matching; borrow method ideas, not unrelated OOC image assumptions |

## 5. Controlled references for future derivations

Useful standard topics for the *companion derivation report*:
- Reynolds transport theorem, differential mass/momentum/species conservation, Newtonian viscous stress and mechanical-energy balance.
- Hele–Shaw/parallel-plate Poiseuille flow and gap-averaging; parabolic moments `1,6/5,54/35`.
- Gradient-vorticity integral identities including boundary terms and nonconstant viscosity.
- Taylor–Aris dispersion for assessing limits of depth-uniform concentration assumptions.
- Optical-flow brightness constancy, Farnebäck polynomial expansion, forward/backward validation, image projection and velocity uncertainty.
- RBF interpolation with and without a divergence-free constraint, cross-validation, conditioning and mask coverage.

Methods in the future PDF are **derived or inferred mathematical models**, not asserted to be equations explicitly published in the 2023 article.

## 6. Experimental data locations (Drive, not versioned by this Git repo)

The project owner's Drive contains the following **verified folders**:

1. [Kristofers_MSc → Raw Images for MSc](https://drive.google.com/drive/folders/1So6iAgNoLnmcELurrMFBTpYVvWVldLjP): `2011-09-09.7z` (~2.846 GB), `2014-04-04.7z` (~1.507 GB), `2014-04-15-Exp2.7z` (~1.182 GB). **Contents not exhaustively checked**; no claim yet that a particular full-cell clip satisfies the no-slip all-liquid criteria.
2. [2WCF-SVD -- Article → Image_sequences → Solidification](https://drive.google.com/drive/folders/1CHVHJiz8jiAXjUvB6Kw5Sz2AiMZm5Cpi): three small filtered-image `.7z` archives. Two previously inspected as usable TIFF sequences, 80 frames at 82x98 and 100 frames at 68x170, but these alone do not supply full calibration and velocity information.
3. [2WCF-SVD -- Article](https://drive.google.com/drive/folders/17k2ncsadc92yJs5A3S264-XkMYXbJejT): contains `Output_2WCF_SVD` and other historical source outputs. Need verify exact run identifiers/PKLs/parameters before numerical comparison.

Raw images and collaborators' datasets may be subject to ownership and redistribution restrictions. Provide synthetic/minimized fixtures in the code repository only after permission.

## 7. Repository handoff and current state

- Original source inventory/audit handoff: [2026-10-22_chatgpt-gpt6_repository-audit.md](../Handoff_file_exchange/2026-10-22_chatgpt-gpt6_repository-audit.md)
- Extended conversation + approved-science handoff: [2026-10-22_gpt6_full-chat_scientific-model-and-documentation-handoff.md](../Handoff_file_exchange/2026-10-22_gpt6_full-chat_scientific-model-and-documentation-handoff.md)
- Agent protocol: [README_for_agents.md](../Handoff_file_exchange/README_for_agents.md)

**Status as of this documentation:** documented but no source-code fixes, real-data flow reconstructions, or experimentally closed energy-budget check.
