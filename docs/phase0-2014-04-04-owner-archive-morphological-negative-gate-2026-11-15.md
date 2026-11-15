# Phase 0 — 2014-04-04 owner-labelled review archive and morphological solid-zone gate

**Review received:** 2026-11-15. **Scientific state:** experiment-owner qualitative preferences and a source-checked **experimental morphology pilot**, not independent solid/liquid ground truth, original v25 temporal MIL reproduction or calibrated concentration. **No source data or existing masks were modified.**

## 1. Original user source and precise semantics

The user provided a 7z archive named \`rewiewed_masks_with_notes_and_labels_READ_ME_inside.7z\` (spelling preserved), SHA256:

\`62a8833a38faf8f38117f7d1c0d3f557355debb57d8e2b73dc06628aa846105b\`.

The uploaded README states:
- green panel frame = better/good result;
- red panel frame = bad/incorrect result;
- no panel frame = neutral/not noteworthy; filename contains additional remarks.

This is **twelve archived objects**, comprising the README and eleven PNG files, including several 3114×1018 or 5439×540 full comparison mosaics and a 1850×605 negative comparison preview. These are **flattened reviewer-marked figures**, not pixel-registered source-coordinate independent phase-mask annotations. The original reviewed PNGs remain private in the chat attachment; no raw images/screenshots are committed to GitHub. Their archival SHA256 and the user-approved border/panel choices are recorded in the new \`docs/phase0_calibration_cases/2014-04-04-owner-archive-panel-label-ledger-2026-11-15.json\` and in the authorized private X: workspace.

### Exact owner preferences extracted from borders and filename notes

| Source | Owner feedback |
|---|---|
| main 0119 positive | Correctly detects no regions |
| main 0480 positive | green t=0.02 and amber expansion; red t=0.04, 0.06, 0.08; t=0.03 unframed/neutral |
| main 0639 positive | filename: t=0.02 looks good, amber expansion correct |
| main 1200 positive | filename: t=0.02 looks good, amber expansion correct |
| main 3147 positive | filename: lower threshold better, amber expansion correct; cyan negative artifacts above solid zone |
| end 0297 positive | filename: t=0.02 looks best, amber expansion correct |
| main 1200 negative | green t=0.04/minarea25; red t=0.08/minarea25 and t=0.05,0.06,0.08/minarea150 |
| main 3147 negative | green t=0.06/minarea25 and t=0.05/minarea150; red t=0.04/minarea25, t=0.08/minarea25, t=0.04/minarea150, t=0.08/minarea150 |
| end 0297 negative | green t=0.04,0.05,0.06/minarea25 and t=0.06,0.08/minarea150; red t=0.08/minarea25 |

**Key update from earlier proposal:** there is stronger owner preference for **positive t=0.02** than t=0.03. This is an *image candidate inclusion* decision, NOT full-solid phase truth or a decision to count ambiguous mushy zones as 100% solid. The previous t=0.04 mask remains a numerical baseline and is never overwritten. Some user choices are nonmonotonic in threshold/area, showing that blindly optimizing image-mask area cannot be grounded in physical truth.

The README also proposes reconstructing a morphologically filled/closed **solid-zone envelope**, then restricting negative-mask fragments to that zone to suppress isolated detections above the front. The user cites Birjukovs, Shevchenko & Eckert, *Experiments in Fluids* 64:131 (2023), DOI [10.1007/s00348-023-03671-2](https://doi.org/10.1007/s00348-023-03671-2), and its open-source implementation.

### Verified original algorithm precedent, not invented equivalence

The authoritative original \`Mathematica_code/Dendrite & Plume Analysis v25.nb\` Git blob SHA \`b13ef6adda22405d89680e3ebe5da50e6f40d297\` contains:
- \`getLiquidMasksWithFilledChannels\`, using \`Closing[...,DiskMatrix@channelClosingScale]\`, \`FillingTransform\`, \`ColorNegate\`, \`ImageSubtract\` and \`DeleteSmallComponents\`;
- \`getLiquidChannels\`, extracting differences between liquid masks with/without filled channels;
- \`getSolidifcationFront\`, with boundary/smoothing/edge/thinning operations.

**The new Python pilot is a separately designed geometry experiment, NOT a fidelity-verified port of these historical Wolfram functions.** Original region boundaries/cell coordinates and actual phase labels are not yet independently admitted.

## 2. Newly executed morphology pilot

Private source:

\`X:\AI-Lab-Test\Solidification_OFV\analysis_outputs\phase0_2014-04-04_targeted_mask_sensitivity_2026-11-15\morphological_zone_pilot_v1.py\`

Versioned source and native tests in this PR:
- \`Python_code/phase0_2014_04_04_morphological_zone_pilot.py\`
- \`tests/test_phase0_2014_04_04_morphological_zone_pilot.py\`

Source identity: original 2014-04-04 radiography archive SHA256 \`77fac9a38a9cdaa41ee5ec9c9562acb7149ee1cee8f0246a80c2b267928f2510\`. Original 761×426 source geometry. The script checks prior benchmark manifests and previously hashed input masks from the fully source-CRC-verified 2014 benchmark. It consumes existing t=0.02 positive candidate masks, t=0.04 negative candidate masks, and **does not regenerate authoritative ground truth**.

Experimental algorithm:
1. Within the original **unapproved** candidate detector rectangle y=[120,412), x=[155,690), binary-close t=0.02 positive candidate regions with disks of radii 4, 8 or 12 source pixels.
2. Keep only connected positive regions near the rectangle's lower edge (bottom-anchored), not disconnected positive upper artifacts.
3. Estimate an approximate first positive position by source column, interpolate missing columns and smooth (median size 15 and Gaussian sigma 2 px). This is a *provisional morphological envelope*, **not a physically measured solid front**.
4. Include all source pixels below the estimated envelope (optional 0,8,16 px upward margin). This creates a **zone**, explicitly **not** a solid-fraction/phase map, and will contain liquid channels/cavities.
5. Keep a **whole connected negative component** if **at least 10 of its candidate pixels intersect the derived zone**. This deliberately preserves a plume-like component's extension above the estimated front if connected to its lower part, unlike hard pixelwise multiplication.
6. When solid-zone anchors are absent (main119/main480), **refuse** to construct a front; never fabricate an all-liquid phase or force a geometric result.

A 3×3 radius/margin sweep, six source-linked frames, yielded 36 meaningful parameter/frame records; early frames were explicitly rejected for insufficient solid anchors.

### Actual negative-mask retention at disk radius 8, margin 8

| Source | Negative pixels before | After | Upper **unapproved** diagnostic strip before → after | Channel-like **unapproved** diagnostic window before → after |
|---|---:|---:|---:|---:|
| main1200 | 432 | 432 | 0 → 0 | 432 → 432 |
| main3147 | 8,326 | 6,839 | **1,698 → 241** | **6,064 → 6,034** |
| end0297 | 8,306 | 8,306 | 475 → 475 | 7,257 → 7,257 |

Thus, in the questionably segmented main3147 upper strip, the candidate filter excludes ~85.8% of upper negative pixels, while preserving ~99.5% of center-channel pixels (6034/6064). It leaves user-favored main1200 and end0297 candidate negative regions unchanged. **This comparison is to existing candidate masks and qualitative user preferences, NOT independently annotated true-phase segmentation.**

Robustness matters: main3147 with radius=8, margin=0 retains only 85 upper-strip negative pixels, while margin=16 retains 1298. Main1200 and end0297 are unchanged across the tested radius 4/8/12 and margin 0/8/16 grid. This sensitivity argues for further spatial/source physics checks before adopting a fixed morphological margin. Provisional front-column medians at margin 8 were approx. source y=319 (main1200), y=149 (main3147), and y=130 (end297). These are **not validated physical interface positions**.

### Actual private outputs

Private root:

\`X:\AI-Lab-Test\Solidification_OFV\analysis_outputs\phase0_2014-04-04_targeted_mask_sensitivity_2026-11-15\`

- \`morphological_zone_pilot_v1\morphological_zone_review_sheet_v1.png\` — original log heatmap and negative mask, green candidate front/envelope, then cyan retained and **magenta rejected** negative features for main1200, main3147 and end297. SHA256 \`25125cb8ec7db7b9d997b8d9a405a7cf9afa9d55b4ef1cb095404ed8f701a185\`.
- \`morphological_zone_pilot_v1\source_zone_sensitivity_v1.json\` — all radius/margin parameter results, SHA256 \`07482EA71BE1B4DDDCB1222126B37DE058A60171A3D0917485B72E6B0E38BC3B\`.
- \`morphological_zone_pilot_v1\*\_radius8_margin8_provisional.npz\` — individually source-coordinate arrays: zone envelope, baseline negative, retained/rejected candidates, estimated front (private, **not** accepted masks).
- \`owner_archive_morphology_review_pack_v1.zip\` — **16-file private ZIP** containing original-resolution per-frame review plots, combined sheet, NPY-derived array bundles, source-parameter JSON and prior qualitative ledger. Integrity check passed; SHA256 \`65ea820f672c4636188b108f93fbe9520900a13c2cd31316a9c843cafe770a3a\`.

The original owner-review 7z archive remains in the chat attachment; the native screenshot PNGs were not transferred to or published on public GitHub. Textual labels/qualitative decisions and original archive SHA are recorded here for provenance.

### Tests and limitations

**Seven synthetic/native Windows Miniconda tests PASS**, including: refusal with missing early solid anchors, shape rejection, correct bottom-connected solid-zone proposal, refusal to follow floating disconnected upper positive regions, retention of a connected negative plume above a candidate front, exclusion of floating upper negative fragments, and non-mutation of inputs. Lightweight Python 3.14 without NumPy/SciPy **skips all seven**; a green CI does not establish a scientific source-validation gate.

Remaining requirements:
- Expert-vetted chamber/sample and actual solid/liquid boundaries for source pixels, as opposed to green/red preferences on flattened montages;
- Case-specific source-time/temperature registration, if interpreting actual front propagation;
- Full v25 native temporal MIL and topology/morphology pipeline validation;
- Explicitly monitor negative false rejection of **real disconnected plumes above the front**, possible false positive bottom-anchored solid-area regions, and loss of gas/metal cavities from geometrical filling;
- Compare hard pixel gating versus whole-component gating in physically reviewed examples;
- Keep 25/5–10/98.6 wt.% chemical endpoints and true attenuation/dark calibration on separate G0 gates.

**No new mask is automatically admitted to production.** The pilot and detailed provenance are on **draft PR #20**, unmerged.

### Preferred 17-file morphology review ZIP

A more reviewer-friendly **V2 ZIP**, retaining every V1 payload and adding a dedicated `MORPHOLOGY_REVIEW_READ_ME_FIRST.txt`, is now the preferred starting point: `X:\AI-Lab-Test\Solidification_OFV\analysis_outputs\phase0_2014-04-04_targeted_mask_sensitivity_2026-11-15\owner_archive_morphology_review_pack_v2.zip` (9,072,413 bytes; SHA256 `c707a4285036829d91d621c31fc535252a86efa980129fc193bfe14df1fce0b3`; 17 entries; ZIP integrity verified). V1 remains archived and was not overwritten. A textual transcription of the uploaded user's original README is also preserved privately as `USER_UPLOADED_REVIEW_README_VERBATIM.txt` in the parent private directory; the source archive image bytes remain in the conversation upload.

**Safety hardening:** the review-code version in this PR explicitly refuses overwriting any pre-existing per-source morphology NPZ reviewer arrays, in addition to refusing overwrite of the existing sensitivity JSON.
