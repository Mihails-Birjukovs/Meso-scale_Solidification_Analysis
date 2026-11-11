# 2026-11-11 production OFV postprocessor code-level regression repair

**Status:** Draft PR #14, **review-required**, no experimental end-to-end validation. **Source:** November 10 direct uploader commit \`297a0a48\` after prior convention correction in merged PR #3. Owner approved repair; original user-edited November 10 preprocessing source and the existing X: data are preserved.

## What was changed

- \`Python_code/VelocimetryRaksturlielumi.py\` explicitly imports the already-merged independent helper \`ofv_coordinate_conventions.py\`.
- Reads \`VelocityInversion\` from the exact upstream \`parameters.json\` and validates finite nonzero value before loading frames. Both saved u and saved v are converted using the **same** upstream inversion and physical pixel-pitch/pair-duration scale (instead of multiplying both by \`delta_x/delta_t\` directly).
- Keeps \`positions_interp\` and \`vectors_interp\` in one coherent image **x-right, y-down** basis. Deletes the later *v-only* reversal on an unchanged y-down grid.
- Computes physical +z vorticity on that grid as \`du_image/dy_image - dv_image/dx_image\`, preserving scalar/velocity coordinate semantics; divergence remains \`du_image/dx_image + dv_image/dy_image\`.
- Adds explicit \`INTERPOLATION_METHOD="rbf"\` default; \`"linear"\` is an opt-in diagnostic/production candidate that is no longer selected silently. The code rejects inconsistent grid shapes, **any nonfinite selected U/V grid cell**, and **any grid cell farther than 2*arrow_step from observed vectors** before downstream gradients and full-domain integrals.
- Records method, upstream inversion, effective-pixel pitch assumption and pair-duration assumption in each summary row, enabling later provenance review.

## Why the guard is conservative

\`griddata(method="linear")\` commonly produces NaN outside the convex hull, and even a finite divergence-free RBF extrapolation outside measured regions can lack physical support. The current "distance less than 2*arrow_step" is an existing *diagnostic threshold*, not an independently validated physical cell wall or confidence mask. The new code therefore **fails closed** on unsupported full-grid physics and must not be bypassed just to produce summary numbers. Future Issue #11/G0 work must add properly registered chamber mask, accepted interpolation support and boundary-flux policy; supporting only interior gradients with masked integration is a separate validated design.

## Reproducible CI checks

New \`tests/test_ofv_postprocessing_regression.py\` performs syntax-safe source inspection without importing the interactive postprocessor, with:
- refusal if both saved velocity components are again converted without inversion, or if only one component is flipped on the y-down grid;
- explicit physical curl helper and selected method/finite/support policy checks;
- manufactured uniform translations for upstream inversion ±1 and all cardinal displacements;
- manufactured asymmetric divergence-free image field \`u=2*y+x/4, v=-3*x-y/4\` for which physical curl +z is **+5** and divergence is zero, including explicit central finite-difference checks;
- fail-fast invalid/missing inversion checks.

The workflow \`.github/workflows/phase0-contract.yml\` runs all tests with Python 3.11, without experimental imaging assets. The **latest PR #14 CI passed** on head \`f02116f8eb75c4e7035a82bb73424d3382e51ab8\` (run 42930249019). This is a **synthetic/static code guarantee only**, not a runtime pass of proprietary \`Divergence_Free_Interpolant\` or a validation of the real 2011/2014 experiments.

## Remaining source-physics admission

- Hardcoded \`delta_x=17.5µm * 4\`, \`frame_rate=5\`, \`bin_factor=5\` and index-sorted PKL/concentration pairing are **not yet tied to an accepted source manifest**. Issue #11 remains OPEN.
- Current postprocessor estimates \`dK/dt+D\`, omitting full Hele–Shaw wall drag, gravity, variable-density terms and boundary flux. This is **not** a closed mechanical energy balance.
- No new frame result can be accepted without source-matched verified original detector data, physical timebase and cell geometry, correct PKL pairs and real experimental rerun. Do **not** close Issues #9/#10 on synthetic tests alone; review actual archived PKL numerical parity first.
- Original 2011-09-09 + 2014-03-07 calibration-workflow limitations remain independently documented in draft PR #15.

**No data were modified or published, and new production-code PR must not merge before user approval.**
