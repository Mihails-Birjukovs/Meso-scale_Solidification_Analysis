# Research-agent handoff — Phase 0 representative radiograph and coordinate correction

**Date:** 2026-11-01 (Europe/Riga)  
**Agent ID:** ChatGPT-GPT-6 / Meso-scale Solidification Analysis / Phase 0  
**Branch:** `fix/ofv-coordinate-signs-phase0-2026-11-01` (proposed; not merged at writing)  
**Base:** `main` following approved PR #2 merge `a955512a00befd5b951eae22e38782917c154a20`.

## User authorization and scope

User explicitly approved PR #2 and requested Phase 0 continuation: a representative experimental image-sequence I/O test, frame ordering, velocity-direction tests, then a **separate focused coordinate-correction PR**. No authorization to merge new PR was given. Preserve upstream code read-only; do not publish its source without redistribution permission.

## Evidence actually obtained

- `main` PR #2 merged and verified.
- Original upstream 2WCF-SVD v4.4 at `pienins/Optical-flow-svd-and-fourier-filtering@27659ae0e0f798189e1fc7c4516453374ad3c9eb`: inspected its input glob, Farnebäck call, forward-backward consistency, confidence filtering and **both-component** `VelocityInversion`.
- The approved user Drive archive `20260331_4 Downsampled ImagesRun1_20260331_v3_3D_filtered_enhanced_KLD_v2_Run1.7z` contains 80 ordered 16-bit TIFFs `Frame_1.tiff` to `Frame_80.tiff`, 82×98 pixels. Extracted read-only into temporary local runtime; staged images to zero-based `filtered3D_00000..00079.tiff` with byte-for-byte SHA-256 checks.
- **Important distinction:** Since an executable pinned upstream checkout was not available locally, the author ran a **source-matched independent diagnostic** with local OpenCV 4.13.0, not an actual execution of the upstream program. It reproduced inspected parameters, forward/backward consistency, median/MAD confidence, 5×5 smoothing and 7-pixel sampling.
- Real-filtered-image sequence: 79 frame pairs, median accepted 96.43% of sample vectors (minimum 57.14%), median apparent speed 0.7179 px/pair, median forward/backward consistency error 0.1140 px; frame mean brightness span 87.24% of mean. These do **not** measure physical velocity without acquisition calibration.
- Ground-truth translations of the real first radiograph confirm direction: +1 pixel right recovered +0.9545 px x; +1 pixel DOWN recovered +0.8968 px image y; −1 pixel UP recovered −0.9577 px image y. The test also covered remaining cardinal/diagonal shifts. Full numbers and caveats: [representative-sequence report](../docs/phase0-representative-sequence-2026-11-01.md).

## Proposed source changes in separate PR

- New `Python_code/ofv_coordinate_conventions.py` makes inversion explicit and testable, providing image-right/down velocity conversion and Cartesian physical vorticity for an image-grid velocity gradient.
- `Python_code/VelocimetryRaksturlielumi.py` uses saved `VelocityInversion` for **both components** prior to RBF interpolation, **removes the old vertical-only reversal** and derives physical +z vorticity with the consistent image-grid reflection. All positions stay in image x-right/y-down coordinates, so image overlays, grid masks and interpolation evaluation remain aligned. The production and hold-out RBFs now receive consistent component conventions.
- Additional tests in `tests/test_ofv_coordinate_conventions.py` cover cardinal motion, inversion=±1, missing invalid inversion, physical vorticity for counter-clockwise rotation, and invariant divergence. The existing Phase 0 GitHub workflow now discovers all offline `test_*.py` files.
- This PR does not change Kristofers' concentration fit, quantitative radiometry, density C03, viscosity models, frame-pair association, RBF algorithm or physical energy validation.

## Remaining blockers and future work

The original 2WCF application has **not** been run on this user-supplied dataset in the current runtime. Exact 2WCF PKL/WXF outputs and same-acquisition quantitative `Conc_In` frames have not been validated together. The processed `Frame_1..80` names do not establish original frame ID, FPS, crop transform or full wall coordinates. Gate G0 remains **open**, and the dedicated source correction PR should not be interpreted as experimental physics validation.

The user-preferred broad research process requires small reviewable branches, date-specific append-only handoffs and no modifications to upstream third-party code. No raw image files should be committed into the public GitHub repository. The remaining practical independent run requires the pinned upstream environment and a known representative calibrated acquisition or appropriately authorized image/PKL data.

This handoff is append-only under `Handoff_file_exchange/README_for_agents.md`; do not overwrite earlier handoffs.
