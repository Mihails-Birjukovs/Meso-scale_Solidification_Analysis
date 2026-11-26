# 2014-04-04 source-locked candidate mask overlay review package

**2026-11-15.** This is a **presentation-only** supplement to the 21-source/756-combination Phase 0 candidate-mask benchmark. It does not revise its mask generator, numerical CSVs, saved binary masks, original Ga–In radiography TIFFs, flat-field acquisitions, or the original Mathematica v25 analysis.

## What was actually generated

The original full-source Ga–In archive was already SHA-verified with SHA256:

\`77fac9a38a9cdaa41ee5ec9c9562acb7149ee1cee8f0246a80c2b267928f2510\`

The authoritative candidate-mask benchmark folder:

\`X:\AI-Lab-Test\Solidification_OFV\analysis_outputs\phase0_2014-04-04_mil_candidate_benchmark_2026-11-14\candidate_sweep_v2_conda\`

was **read only**. Its manifest, all **18 existing binary PNG mask SHA256s**, 111 original \`Reference\` flat-field TIFF member CRC32s, 80 initial experimental TIFF member CRC32s and six selected original source TIFF member CRC32s were rechecked. All 18 masks then passed a **pixel-for-pixel equality check against independently recalculated Gaussian-1px / log contrast 0.04 / 4-connected component area >=25 masks**. The original scientific benchmark's outputs were not changed.

Six original experimental frames form the human review set: **main ordinals 119, 480, 639, 1200, 3147, and end ordinal 297**, all in original 761 x 426 detector coordinates (top left origin, x right, y down). Their original source filename and candidate clock are listed in the overlay manifest; the clock is not an independently accepted acquisition time.

Per source frame, five **native detector-size, RGB PNG** variants were generated:
1. provisional heatmap \`-ln(I_original/J0_candidate)\`, where \`J0_candidate\` is the first 80 original **main experiment** TIFFs' pixelwise median, **not** a \`Reference\` acquisition;
2. red **positive candidate** mask outline;
3. cyan **negative candidate** mask outline;
4. red and cyan combined outlines;
5. red and cyan combined outlines with **24% transparent fill**.

A one-source-pixel dark halo surrounds each colored boundary so that the red boundary is visible on red heatmap regions. The diverging heatmap uses the same **fixed [-0.12,+0.12] color scale for all frames**. Nonsaturated original detector pixels retain native spatial mapping; invalid detector pixels are shown dark grey. Each selected frame has a five-column comparison PNG, and a **six-frame, five-column contact sheet** aggregates the complete review set.

**Total generated images:** 30 native 761 x 426 overlay/heatmap files + 6 per-frame five-column review sheets + one aggregate contact sheet = **37 PNG files**, plus the machine-readable provenance manifest.

## Actual output paths and hashes

All assets remain private in the user's authorized X: workspace:

\`X:\AI-Lab-Test\Solidification_OFV\analysis_outputs\phase0_2014-04-04_mil_candidate_benchmark_2026-11-14\review_overlays_v1\`

- \`review_overlay_contact_sheet_v1.png\` — SHA256 \`27de3301b88845e96ea0e6dbe518a271881ff960c296e113619f55c6ac9f6331\`.
- \`review_overlay_manifest_v1.json\` — SHA256 \`4a5acd980f6e2c328c8401130520fe460f2074b26360fcbe16f75859b332dcff\`. It contains individual SHA256s for all 37 images, full source identifiers, positive/negative source-mask hashes, overlay settings and explicit physical refusal flags.
- \`review_overlays_v1.zip\` in the **parent benchmark directory**, compressed review package, **27,811,612 bytes**, SHA256 \`1e9453486f998f255227fb83947e3e9d70b7344552a1741f65be82dec5ba6a5b\`.

The source generator is \`Python_code/phase0_2014_04_04_review_overlays.py\` in this development PR, with the original executed file retained privately as \`create_source_locked_review_overlays_v1.py\`. The script is deliberately case- and workspace-specific: it reads the already admitted private archival records and **refuses an existing destination** rather than silently overwriting a reviewer pack. Replay must use a fresh output directory or an explicitly versioned output; never overwrite the original artifacts.

## Scientific boundaries and reviewer workflow

**Important:** Positive and negative **candidate intensity anomalies are not automatically solid and liquid phases**, nor are they calibrated Ga-rich plumes. The analysis rectangle y=[120,412), x=[155,690) is still an **unapproved candidate detector ROI**. The overlaid contours are **not expert-annotated chamber boundaries, true phase fronts, independent ground truth or a full historical v25 dynamic-MIL threshold replay**.

The flat-only correction choice remains the operational diagnostic policy. The raw \`Reference\` TIFFs are **owner-confirmed detector flat fields R**, not a homogeneous 25 wt.% initial specimen baseline. No validated dark offset, physical camera clock, sample chemistry or optical-density-to-\`C_In\` calibration has been admitted.

Recommended review order: first \`review_overlay_contact_sheet_v1.png\`; then the per-frame \`*_all_views.png\` sheets to inspect early/onset/established/late structures at full resolution; then single-polarity \`*_lnJ0_outline_pos.png\` and \`*_lnJ0_outline_neg.png\` files when a contour is hard to distinguish. Save independent conclusions separately in the existing unfilled \`EXPERT_REVIEW_2014-04-04_SOURCE_UNFILLED.csv\`—do not edit the generated masks.

**Quality evidence:** 6 of 6 new synthetic native tests passed with compatible Miniconda NumPy 1.26.4, SciPy 1.13.1, Pillow 8.4.0 and Matplotlib 3.5.0. Tests check exact one-pixel contours, red/cyan assignment, fill opacity, original pixel geometry, preservation of unmasked pixels, clear invalid pixels and mask SHA refusal. The actual source-run verified **all six CRC-checked TIFFs and all 18 mask equality conditions**, not just synthetic fixtures. Lightweight CI lacking image libraries may skip native image tests; it does not establish human phase validation.

**Approval status:** the user approved generating this **review aid**. The masks, sample ROI, phase assignments, full native v25 algorithm and chemical calibration still require independent acceptance. This add-on is committed to the existing **draft PR #20** for traceability, with no merge into \`main\` unless separately authorized.
