# Supplement — two additional original reference/dark pairs and PR #7 cross-check

**Date:** 2026-11-02, append-only follow-up to `2026-11-02_gpt6_complete_background_means_and_kmedoids.md`. PR #7 draft branch `feat/phase0-reference-stacks-kmedoids-2026-11-02` remains owner-review only.

## Extended raw-archive source inventory

Original `2011-09-19.7z` contains an original full-size `2011-09-19/2011-09-19` branch plus `2011-09-19/2011-09-19-cropped-left-side` derived image copies; naive `ga-25in-ref1` and `ga-25in-dark1` prefix counts are **202 each**, but exact full-size *original* paths contain **101 ref1 and 101 dark1**. Do not mix cropped duplicates in original means. Separate `ref2` also exists and was not combined with `ref1`.

`2013-01-10.7z` contains 103 `ref1`, 103 `dark1`, 112 `ref2` and 103 `ref3` TIFFs; only original `ref1+dark1` used in this reconstruction, other reference groups remain separate pending experiment identity. `2011-09-09` has 214 reference TIFFs but no dark stack detected; `2014-04-04` 111 reference TIFFs and no dark stack detected. `2014-04-15-Exp2` has 108 source `ref2` + 120 `dark2` even though dark files sit under a folder named `Reference`.

## Completed outputs from exact hash-verified PR #7 script

The generic `Python_code/phase0_reference_dark_reconstruction.py` file from the actual PR branch was downloaded to authorized X: workspace, verified original Git blob SHA **0539407659e93dec9f4173a8bf23438dbdf751ef**, then executed directly on original TIFF copies, preserving source inputs.

| Original selected source | Ref | Dark | Source pixels | Mean R counts | Mean D counts | Valid R>D fraction |
|---|---:|---:|---|---:|---:|---:|
| `2011-09-19` original `ref1+dark1` | 101 | 101 | 755×444 | 54106.876 | 53218.198 | 0.6535 |
| `2013-01-10` original `ref1+dark1` | 103 | 103 | 756×542 | 57247.210 | 54911.807 | 0.6780 |
| `2014-01-15` `ref1+dark1` (initial stand-alone implementation) | 113 | 105 | 760×560 | 58230.418 | 55592.473 | 0.7230 |
| `2014-04-15 Exp2` `ref2+dark2` | 108 | 120 | 762×499 | 57847.084 | 54317.608 | 0.7722 |

All three PR #7 generic executions generated reference mean, dark mean, R-D float32 grayscale TIFFs, plus `manifest.json` containing individual raw TIFF SHA-256 and frame mean/saturation statistics. Existing local `2014-01-15` original prototype outputs were independently imported by local Mathematica with numerically confirmed means; generic code synthetic tests were added to repo.

**Byte-for-byte cross-script parity, 2014-04-15 Exp2:** both PR #7 generic and the original local stand-alone prototypes produced identical reference and dark TIFF SHA-256:
- Reference: `ab868a99d6db977b73775efbae1b146bb5f243fc567b1b3e1b0b07b558cc2d91`.
- Dark: `235cfb0812e58fc06bf6a4ecda71e5c169d0d704ad1347d6b3ff393fe30fb946`.

Full report and remaining source-admission gaps: `docs/phase0-reconstructed-backgrounds-and-kmedoids-2026-11-02.md`.

**G0 remains OPEN:** no per-acquisition physical ROI/crop map, signed dark/reference detector stability, validated MIL solid-vs-liquid segmentation, chemical anchor placement, camera log, or same-source quantitative OFV/concentration temporal+spatial pairing has been accepted.
