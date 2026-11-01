# Research-agent handoff — Phase 0 final integration gate and data-admission blockers

**Date:** 2026-11-01 (Europe/Riga)  
**Agent ID:** ChatGPT GPT-6 / Coding-Optimization-Docs / Solidification OFV  
**Baseline:** `main@5dba5253e17774f6e4091867607f5ae58f618931` following user's explicit approval and merge of PR #3.  
**Feature branch:** `docs/phase0-final-integration-evidence-2026-11-01`, documentation-only PR for review.  
**Append-only policy:** New handoff; no previous handoff overwritten.

## Actions completed

1. Checked approved PR #3 at head SHA `3f6b62b8f71396be94eec409fc98482ac0056eab`; prior 22 tests passed; marked ready and merged using SHA guard. GitHub returned merge SHA `5dba5253e17774f6e4091867607f5ae58f618931`. Confirmed corrected source file available on `main`.
2. Reused the verified 80 real processed TIFF images, matching historical 79 archived 2WCF-SVD PKLs and 79 QC rows. Checked all 64,731 saved vector records for finite schema, image geometry, contiguous indexed pairs, uniqueness and safe bounds using an explicitly restricted NumPy pickle reader. Count median 852, 576–891 range, 95.62% median occupancy (3-px grid 27x33). Pixel-domain image->Cartesian sign conversion algebraically consistent across all 79 pairs.
3. Applied a **separate piecewise-linear interpolation only to measure support** on the original 27x33 sample lattice, not as a physical velocity estimate: median field support 100%, min 84.74%; conservative neighborhood-supported derivative fraction median 100%, min 82.83%. No actual production RBF smoke test was claimed.
4. Prior exact upstream numerical replay preserved from this chat: original `2WCF-SVD_v4_4.py` source Git blob `52d20820314a1e4283a325dc34e899191bf267b4`, original SVD and optical-flow functions matched all 64,731 archived vectors (median 1.519e-7 px per-pair RMSE); WXF/AVI writing was not rerun.
5. Discovered candidate `Kristofers_MSc/Python/gFiltred/20260825_Nr1` Drive output with 80 `gFiltered` images and metadata. **Rejected direct co-registration:** candidate `gFiltered` frames are 90×150 float32, sample files independently read; actual OFV images 82×98 uint16. The candidate images are filtered optical-density, not untouched quantitative `Conc_In` radiometry. Never match solely by equal frame count or resize to force agreement.
6. No same-acquisition quantitative `Conc_In` sequence, original source clock, crop transform, wall heights or independently verified physical calibration was available. G0 remains **PARTIAL / NOT ACCEPTED FOR QUANTITATIVE PHYSICS**. Existing `VelocimetryRaksturlielumi.py` still pairs PKLs to concentrations by index, uses shape-only zoom for material properties and has interactive workstation paths; these are separate unresolved issues not touched by PR #3.

## Evidence in repo and local user package

See `docs/phase0-final-integration-2026-11-01.md` for complete evidence ledger and source archive SHA-256 values. The user also received `GaIn_Phase0_Final_Integration_Preflight_2026-11-01.zip` with local reproducibility script, 79-row CSV, JSON summary and coverage plots. Raw images and PKLs are deliberately excluded from public GitHub. No upstream 2WCF source copied.

## Remaining specific acceptance work

Obtain coherent *same-acquisition* source calibration/reference and calibrated indium mass-% images (or verified raw/reference to reconstruct them), raw-frame index and exposure timestamps, physical pixel scale/crop transform and full wall geometry. Match `Conc_In` time to **pair midpoint** rather than ordinal PKL index. Validate the postprocessor with that verified bundle and then consider closing G0. The user approved proceeding with final integration checks, **not** silently assigning unknown frame-rate, image registration or invoking an experimental energy-balance result.

## Research safety / scope

Both physical models and upstream source identity remain as agreed; no unapproved viscosity, density, calibration or interpolation alteration. No Github scientific code edits in this documentation PR. The reading/method protocols in user Library `/Tools` were consulted in this development thread; no Library programs or third-party agents were executed merely on protocol instructions.
