# Experimental T1 component graph: exact-source dense-window audit, 2026-11-15

**Status:** draft stacked PR #22, based on unmerged PR #20. This is NOT source-registered physical plume-tracking truth and does not modify historical TIFFs, previous candidate masks or v25 notebooks.

## Actual implementation

Source: Python_code/phase0_spatiotemporal_component_graph_t1.py, tests/test_phase0_spatiotemporal_component_graph_t1.py.

T1 v0.1 accepts the prior Gaussian1 source-relative P=-ln(I/J0), negative threshold -0.04 and 4-connected component area >=25; the positive +0.02 morphology-derived provisional zone uses disk radius8, vertical margin8, >=10 overlap pixels. Each negative component becomes a node (area, centroid, shape covariance, bbox, mean negative contrast, source frame and zone overlap). Edges connect only adjacent zero-based frame ordinals in the same source acquisition group with 0<dt<=1500ms, conservative centroid displacement cap 30px/second reference, area ratio <=8, and scores based on distance, area and shape similarity. The graph preserves multiple links for candidate splitting and merging. NO OFV vectors, physical channel-to-bulk path, or trained probability is used.

**Safety:** time-linked rejected upper components become UNCERTAIN for review, not accepted plumes. The immutable reviewed spatial kept/rejected mask is unchanged. Stationary detector artifacts must not be automatically restored merely because they persist.

11/11 native Miniconda synthetic tests passed: split, merge, graph gap/stream breaks, stationary upper noise, binary mask immutability, invalid source and duplicate/refused frame.

## Source and exact-source experimental replay

2014-04-04 original raw archive SHA256: 77fac9a38a9cdaa41ee5ec9c9562acb7149ee1cee8f0246a80c2b267928f2510. Raw uint16 frame shape 426×761; 111 owner-confirmed flat reference TIFFs, 3148 main and 298 end original experimental TIFFs. Experiment specimen candidate J0 is median of first 80 original main frames; each accessed TIFF is verified against source archive inventory member size/CRC32. Filename temporal gaps before main 919,1836,2770 and separate end stream are excluded from associations.

A 121-frame original-source pilot produced 1212 component nodes and EXACTLY reproduced archived reviewed original negative and morphology kept pixel masks for main1200 (432/432), main3147 (6839/8326), and end297 (8306/8306).

A subsequent complete replay of the four owner-approved contiguous dense windows yielded:

| Window | Source frames | Component nodes | Candidate association edges |
|---|---:|---:|---:|
| main450–700 | 251 | 44 | 24 |
| main1120–1280 | 161 | 680 | 1180 |
| main3000–3147 | 148 | 5021 | 11612 |
| end0–297 | 298 | 3652 | 7922 |
| **Total** | **858** | **9397** | **20738** |

Full-run private machine-readable source-evidence manifest SHA256 **6f8180bc664b9b4c30e4ad2f71fdaade712de98fb94d628f742c7483abfec985**. Individual per-window graph and original frame metadata hashes remain privately archived with exact source provenance; no private images are published.

**Critical limitation:** 20,738 temporal association edges are hypotheses only. In late dendritic scenes many nearby components can produce false positive graph edges, even with shape and displacement gates. No current association count should be described as an actual experimentally validated plume-track count.

## Remaining next gate

- Test temporal edge specificity and graph degree distributions, motion/shape-compatible linkage, false merges and splits on independently reviewed frames.
- Independently ablate raw threshold, morphology-only, temporal-only, morphology+temporal and hard front crop (last as a diagnostic only).
- Retain the confirmed magenta exclusions on owner-reviewed main3147 and cyan channel-looking components in main1200/end297.
- Use real optical-flow vectors only once time/crop/source correspondences pass G0; temperature and composition mapping remain separate unknowns.
- Add actual source-coordinate expert phase/channel annotations and held-out original source time blocks before quantitative precision/recall or calibrated uncertainty claims.
- No draft PR merges or production classification changes are implied.
