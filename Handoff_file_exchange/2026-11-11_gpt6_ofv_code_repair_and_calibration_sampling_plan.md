# 2026-11-11 — PR #13 merged; code-level repair of November 10 OFV regressions

**Owner approvals:** PR #13 explicitly reviewed/approved and merged at `568522928c68616592c2b35e90862bef80316bce`. Owner explicitly approved repairing production OFV postprocessing and G0 physical registration work. **Draft PR #14** (`fix/ofv-physical-conventions-and-field-admission-2026-11-11`) is new and must **not** be merged without later approval.

## Changed code in draft PR #14
- Imports preexisting approved `ofv_coordinate_conventions.py`.
- Requires upstream `VelocityInversion` and divides **both** saved u/v components by it, keeping image x-right, y-down coordinate system until physical-curl projection; deletes v-only sign flip.
- Physical curl `omega_z=du_image/dy_image-dv_image/dx_image`; velocity divergence remains image-frame `du/dx+dv/dy`.
- Explicit `INTERPOLATION_METHOD="rbf"` default, only user edit selects linear; conservative selected-grid shape, no-NaN and max observed-support-distance refusal before full-field physical gradients/integrals.
- Adds method, inversion and **assumed** effective pixel pitch and pair duration to summary CSV rows. Notes those assumptions are **not** actual source clock acceptance.
- New `tests/test_ofv_postprocessing_regression.py`: 9 static/manufactured tests including 2D asymmetric u/v with positive physical curl 5 and zero divergence, finite-difference derivative checks and both inversion values.
- New `docs/phase0-ofv-postprocessor-repair-2026-11-11.md` scientific change/limitation audit.

**Initial verified CI:** GitHub Actions `42930249019` passed at earlier code head `f02116f8...`; most recent documentation-only additions require latest CI recheck before reporting whole PR pass. **No original PKL or real experimental velocity/concentration frame has been rerun** in the connected workstation environment. Keep Issues #9/#10 open pending actual PKL replay and Issue #11 pending source time/crop geometry.

## Calibration protocol parallel work

**Draft PR #15**, independent of the OFV repair, records detailed source-grounded calibration-protocol plan:

- initial homogeneous **pre-solidification** 25 wt.% In = `P=0` after dark-corrected temporal baseline, separate no-dark comparator;
- late coarsened **full-cell-thickness** primary In-rich dendrites around 98.6 wt.% (as assumed in Shevchenko note), selected using v25 MIL+clean skeleton+grain masks, robust high-attenuation *interior plateaus*, not max pixels;
- **Ga-rich channel** 5–10 wt.% In as original reference, supported by separate liquid-gallium cell; liquid-only KMedoids identifies potential plume cores but extreme medoid class alone **cannot be labelled 5%**;
- full visible-frame source/detector validity, phase/path-length and rho-dependent attenuation uncertainty, source-matched measurement anchor masks, held-out branch/core/time validation.
- *Ambient initial* means 25% only before segregation; later bulk concentration evolves and is measured, not hardcoded.
- 2014-03-07 case: 500 processed 567x276 TIFFs, 418 algorithmic 763x384 solid masks, source IDs 600..2685; lacks accepted crop transform and original 2014 beam/dark/pre-cooling raw frames, so current status segmentation benchmark, **not accepted absolute C(P) calibration**.
- Reference methods: `Mathematica_code/Dendrite & Plume Analysis v25.nb`, 2023 methods paper; Natalia Shevchenko `Concentration_mapping_intermediate.docx` in Project file corpus, not redistributed in GitHub.

**Reproducibility:** Consulted the active Library `/Tools` router v1.0.1 and Wolfram Engineering current README/protocol, preserving .nb source authority and synthetic-vs-experimental distinction. Any historical uploads which have expired are irrelevant to immediate repo/X: work; reupload only if a specific missing attachment is needed.

**Next:** owner review of PRs #14 and #15; real source/timing/PKL field acceptance, 2014 image-mask transformation, MIL skeleton and plume-run validation with held-out manually annotated masks. Do not claim G0 closed or energy-budget closure.
