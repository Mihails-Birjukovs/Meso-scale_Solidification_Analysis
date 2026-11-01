# Meso-scale Solidification Analysis — Technical Documentation

**Documentation baseline:** 2026-10-22. **Status:** Read-only technical/scientific audit and approved *design*, not a claim that planned code revisions have been implemented.

This documentation explains the current public repository, experimental methodology and publications, software interfaces, verified problems, and the future validation framework for composition-aware optical-flow velocimetry (OFV) in Ga–In Hele–Shaw cells.

## Start here

| Document | Purpose |
|---|---|
| [Historical v24 MIL / plume example provenance](phase0-historical-v24-mil-plume-example-audit-2026-11-02.md) | Experimental MIL overrides, K-medoids/denoising settings, archived overlays and source-mask registration gates |
| [Phase 0 full raw reference/dark reconstruction & K-medoids sweep](phase0-reconstructed-backgrounds-and-kmedoids-2026-11-02.md) | Dataset-specific notebook pixel/exposure metadata, 2 reconstructed detector means, archived-average mismatch, K=9/16/24 tests |
| [Phase 0 notebook segmentation and time registration](phase0-plume-segmentation-timing-g0-2026-11-02.md) | Original v25 MIL/KMedoids mechanism, comparative radiometry, timestamp gating, and outstanding G0 criteria |
| [Phase 0 historical raw TIFF and timing audit](phase0-historical-raw-radiometry-2026-11-01.md) | 2011 source example, 2014 dark/reference sensitivity, nominal 1-Hz raw timestamp checks and G0 blockers |
| [Phase 0 expanded Drive dataset census](phase0-drive-dataset-census-2026-11-01.md) | Alternative processed series, raw MSc archive transfer limit, and archived PhD field comparisons |
| [Phase 0 final integration preflight](phase0-final-integration-2026-11-01.md) | Verified all 79 archived vector outputs, candidate concentration rejection and remaining G0 admission gates |
| [Representative OFV image-sequence evaluation](phase0-representative-sequence-2026-11-01.md) | 80 real filtered frames, synthetic translation controls, tested sign conventions and G0 gaps |
| [Phase 0 OFV interface contract](phase0-ofv-integration.md) | Pinned 2WCF-SVD source, rights, TIFF staging, coordinate/time manifest, verification gates |
| [Architecture and workflow](architecture-and-workflow.md) | Current ownership of each notebook/script, two distinct image branches, interfaces to read-only 2WCF-SVD, provenance and time/coordinate conventions |
| [Current source inventory](current-code.md) | What each current file *actually* does, and methodological relationship to the 2023 publication |
| [Scientific methods and proposed physics](scientific-methods.md) | X-ray attenuation, mass-fraction mixing, mass continuity, quasi-2D gap profile, gradient/vorticity/Q, energy and enstrophy identities |
| [Confirmed issues and uncertainty register](known-issues.md) | Prioritized bug reports, scientific limitations, test status and evidence required |
| [Validation protocol and roadmap](validation-roadmap.md) | Synthetic controls, OFV filtering variants, three interpolators, mass/energy checks, acceptance criteria and development sequence |
| [Literature, data, and provenance](references-data.md) | Publication, supplement, external dependencies, upstream repository and experimental Drive archive inventory |

## Important boundaries

- **Active code for next development phase:** `Python_code/ImagePreprocessWithReference.py` and `Python_code/VelocimetryRaksturlielumi.py`.
- **External, read-only upstream estimator:** [pienins/Optical-flow-svd-and-fourier-filtering](https://github.com/pienins/Optical-flow-svd-and-fourier-filtering), `2WCF-SVD_v4_4.py`. Do not edit as part of this project.
- **Original published baseline:** Mathematica notebooks are retained for the established solidification segmentation/morphology methodology; `OFV_field_postprocessing_v2.nb` is a legacy/check-up artifact, not the main active flow postprocessor.
- **Research model:** Single miscible binary Ga–In liquid, Newtonian, composition-dependent mixture properties; all-liquid interval initially; constant 0.15 mm Hele–Shaw gap with parabolic profile; x-right/y-up physical axes. Thermal-property dependence and pressure-dilatation are deferred assumptions, not proven absent.
- **Scientific validation:** Synthetic numerical tests were run separately; no experimental flow-energy closure has yet been shown. An energy residual is a *falsification/consistency* diagnostic, not a unique proof of correct OFV.
- **Data:** Experimental images, reference/calibration records and OFV PKLs are not tracked in this source repository.

## Distinguishing evidence levels

Throughout these documents:
1. **Current source** means implemented/visible in the public repository at the reviewed date.
2. **Published method** means supported by the cited article/supplement.
3. **Agreed model** means an approved approximation for future analysis, not an empirical verification.
4. **Planned** means **not implemented** in the two active Python files.
5. **Synthetic verified** refers only to the separate small test-only Python prototype, 17 tests passing on 2026-10-22, not to this repository's CI or real measurements.

## Research-agent collaboration

Consult [`Handoff_file_exchange/README_for_agents.md`](../Handoff_file_exchange/README_for_agents.md) and the [dated full-chat handoff](../Handoff_file_exchange/2026-10-22_gpt6_full-chat_scientific-model-and-documentation-handoff.md). Handoff files are append-only. The main source code has not been changed by this documentation effort.

## Reader orientation

Begin with [architecture](architecture-and-workflow.md) if you want to run experiments, [scientific methods](scientific-methods.md) if you need the model, and [issues](known-issues.md) followed by the [roadmap](validation-roadmap.md) if you want to implement or review changes.

**Companion report:** A separate, pedagogical PDF derives the proposed equations step-by-step; the PDF is exported to the project owner outside GitHub and is not represented here as an executable or already validated physical model.
