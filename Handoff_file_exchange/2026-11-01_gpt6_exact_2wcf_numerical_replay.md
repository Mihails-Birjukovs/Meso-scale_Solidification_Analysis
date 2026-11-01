# Agent handoff supplement — exact original 2WCF numerical core replay

**Date:** 2026-11-01 (Europe/Riga)  
**Agent:** ChatGPT GPT-6 / Meso-scale Solidification Phase 0  
**Branch:** `fix/ofv-coordinate-signs-phase0-2026-11-01`, draft PR #3  
**Append-only:** Earlier dated handoffs from 2026-11-01 remain untouched. This is new additional evidence.

## Resolved execution obstacle

A user-authorized Drive copy of `2WCF-SVD_v4_4.py`, ID `1NeCn2W6csCIdjZuybL6YPF-yhD4xzVOD`, was obtained. Its Git blob SHA **52d20820314a1e4283a325dc34e899191bf267b4** exactly matches the previously inspected upstream commit `27659ae0e0f798189e1fc7c4516453374ad3c9eb`. Thus the numerical algorithms were available locally without cloning or modifying the external GitHub repo, and without copying source into this public GitHub repository.

The local Python environment lacked `wolframclient`, so a non-calling import shim for `wolframclient.serializers` was used; no WXF export was attempted. All original input filtering and numerical computation used **unmodified** upstream functions `svd_filter_images` and `compute_flow_pair`.

## Exact input/settings

Used original 80 TIFF frames `Frame_1.tiff ... Frame_80.tiff` (82×98 px), from Drive input archive `1tnxbxv2BI5F0RDWF0oF3mBI7YPfsq3l-`. Actual historical 2WCF output archive `1A7fBi_jZDlzHCoZvJAjPXFP3O0ngusjn` supplied a historical `parameters.json`: `USE_SVD=true`, `KillIDs=[0]`, `ArrowDensityStep=3`, `VelocityInversion=-1`, `MedianOfMeansGroupSize=1000`, plus the other confidence smoothing and Farnebäck parameters. No guessed defaults.

## Original numerical core output compared against archived results

- Every one of **79/79** adjacent-image flow pairs was independently computed.
- The exact saved sparse-vector locations matched across **64,731/64,731** vectors (100% overlap).
- Median of per-pair RMS vector differences: **1.5191944×10⁻⁷ pixels**; 95th percentile **3.2927632×10⁻⁷ pixels**.
- Median of per-pair mean absolute vector differences: **6.1562974×10⁻⁸ pixels**.
- Median rerun forward/backward consistency error **0.1191105768 px**, compared with archived **0.1191105694 px**.
- Local environment: OpenCV 4.13.0, NumPy 2.3.5.
- Original optional WXF and AVI serialization/presentation pipeline **was not rerun**. Code provenance of the *historic* archive is not separately recorded in its parameters.json despite near-numerical-identity with the hash-verified contemporary source.

**Result:** strong numerical reproducibility of the original 2WCF **flow and SVD filtering core**, now supporting the sign fix proposed in PR #3 and the provenance requirements of Phase 0. This is stronger than the previous source-matched independent OpenCV experiment, which remains separately documented.

## Remaining acceptance gates

G0 remains **PARTIALLY VERIFIED**, not complete. The exact original raw-to-processed frame timing, acquisition source indices, geometric crop offsets, independently calibrated concentration `Conc_In` fields for the same image sequence, and physical wall/domain orientation must still be verified before a reliable Ga–In mass/energy budget. The postprocessor remains tied to interactive Windows paths and the old index-based PKL/concentration matching, which are not corrected by PR #3.

The same executable upstream source file was **not copied to the public solidification repo**; upstream redistribution rights still require explicit authorization. All archived images/PKLs stayed out of GitHub.

See `docs/phase0-representative-sequence-2026-11-01.md` (feature branch, updated) for both the initial source-matched checks and the full exact-core replay metrics.
