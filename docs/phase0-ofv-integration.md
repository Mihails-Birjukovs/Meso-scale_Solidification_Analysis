# Phase 0: 2WCF-SVD input/output contract and independent test plan

**Status:** feature-branch implementation; not merged or validated on real Ga-In images. This document supplements [the approved roadmap](validation-roadmap.md).

## Upstream source and license gate

- Reference: https://github.com/pienins/Optical-flow-svd-and-fourier-filtering
- Inspected commit: **27659ae0e0f798189e1fc7c4516453374ad3c9eb** (2026-09-22).
- Source: https://github.com/pienins/Optical-flow-svd-and-fourier-filtering/blob/27659ae0e0f798189e1fc7c4516453374ad3c9eb/2WCF-SVD_v4_4.py
- Blob SHA: **52d20820314a1e4283a325dc34e899191bf267b4**.
- The script credits Ansis Z (main developer) and Mihails B (co-developer).
- The upstream tree has no LICENSE file or explicit redistribution grant. It is public for reading, but public visibility does not by itself authorize republishing a vendored copy. **No upstream source is copied here.** Obtain explicit permission/license before revisiting that approach.
- A **separate local checkout** pinned at the commit above is the recommended first practical OFV runner. Upstream currently contains hard-coded Windows run paths; this branch does not modify the upstream source.
- Upstream flowenv_setup.txt proposes Python 3.10, NumPy 1.26.4, OpenCV 4.5.5.64 headless, and imageio, pandas, matplotlib, tifffile, scipy, tqdm and wolframclient. Environment acceptance is not verified here.

## Confirmed input/output contract

| Interface | Current source behavior | Phase 0 action |
|---|---|---|
| Motion-image exporter | filtered3D_00000.tif etc. | Stage **byte-identical** copies with .tiff suffix in a separate empty folder |
| Upstream TIFF input | Loads only .tiff files, sorted numerically | Assert unique zero-based contiguous frame IDs |
| Upstream OFV output | One velocity_field_00000.pkl per consecutive pair; keys x,y,u,v | Check filenames/counts; do not automatically unpickle |
| Auxiliary upstream outputs | WXF vectors, parameters.json, flow_qc_metrics.csv, preview AVI | Retain as run provenance |
| Upstream VelocityInversion | Multiplies **both** image-forward flow components before saving; default -1 | Undo when constructing forward physical velocity |
| Concentration product | Conc_In_00000.tif for every preprocessed image; In wt.% | **No histogram matching, relabeling or renormalization** |
| Current downstream code | Independently flips only v after reading saved vectors | Not changed here; fix coherently in a later PR |

## Time convention

Raw exposure-center times are t_j = acquisition_t0 + j * raw_dt. For nonoverlapping B-frame bins starting at raw source index j0, the bin center of output i is

    T_i = acquisition_t0 + [j0 + i*B + (B-1)/2] * raw_dt .

Upstream velocity index i corresponds to input images i and i+1. Its nominal center time is

    T_flow_i = (T_i + T_(i+1))/2 .

Example raw_dt=0.2 s, B=5, j0=0: T0=0.4 s, T1=1.4 s, T_flow_0=0.9 s. These times are conditional on an independently verified source frame index and acquisition clock.

## Coordinate convention

OpenCV images: x-right, y-down; forward flow is image-pixel displacement from earlier to later frame. Underlying 2WCF-SVD converts both components with a configurable inversion before writing PKL:

    u_saved = inversion*u_image_forward
    v_saved = inversion*v_image_forward

To get physical x-right/y-up motion in the cropped image pixel-center frame, for effective pixel pitch s, image height H and image pair interval dt:

    x_m = x_pixel*s
    y_m = (H-1-y_pixel)*s
    u_m_s = (u_saved/inversion)*s/dt
    v_m_s = -(v_saved/inversion)*s/dt

The physical global origin, crop offset and full image height remain separate calibration requirements for full-cell potential energy.

## Standalone utility and tests

- [Python_code/phase0_contract.py](../Python_code/phase0_contract.py) is a **standard-library-only** metadata/contract checker. It imports neither the upstream program nor any arbitrary pickle. It refuses gaps/duplicates, inconsistent image/concentration counts and nonzero-flow-pair count mismatches.
- [tests/test_phase0_contract.py](../tests/test_phase0_contract.py) verifies time and coordinate sign conventions, file integrity in .tiff staging, and metadata admission/refusal.
- [.github/workflows/phase0-contract.yml](../.github/workflows/phase0-contract.yml) runs the tests under Python 3.11 on a controlled feature branch or PR.

Example commands from the solidification repository checkout (substitute experiment-specific paths):

    python Python_code/phase0_contract.py --images /path/to/filtered3D --concentration /path/to/Conc_In --raw-dt-s 0.2 --bin-size 5 --source-start-index 0 --pixel-size-m 0.000070 --velocity-inversion -1 --stage-tiff /path/to/EMPTY_2WCF_input --manifest-out /path/to/phase0-manifest.json

    python -m unittest discover -s tests -p "test_phase0_*.py" -v

## Running OFV through the pinned external checkout

[Python_code/run_2wcf_external.py](../Python_code/run_2wcf_external.py) is an original **launcher** that imports the pinned 2WCF-SVD implementation from an external local checkout. It avoids changing upstream hard-coded run paths and keeps the source separately installed. It **does execute** the audited third-party script in your environment, so only use a checkout whose SHA and content you trust; its preflight refuses any commit/blob mismatch. The launcher requires the upstream numerical dependencies, including wolframclient for WXF output. It has not yet been run on experimental images.

    git clone https://github.com/pienins/Optical-flow-svd-and-fourier-filtering /path/to/2WCF_external
    git -C /path/to/2WCF_external checkout --detach 27659ae0e0f798189e1fc7c4516453374ad3c9eb

Run from a trustworthy Python environment with the upstream requirements installed:

    python Python_code/run_2wcf_external.py --upstream-checkout /path/to/2WCF_external --images-tiff /path/to/EMPTY_2WCF_input --output /path/to/NEW_2WCF_run --arrow-step 7 --velocity-inversion -1 --video-fps 1

The image folder must contain staged .tiff frames; the output folder must be new or empty. The launcher produces PKL, WXF, upstream QC and parameter snapshots, plus a provenance summary, with serial computation by default. It does **not** change upstream flow computation or interpolate density. The video frame rate must reflect the binned images; in the initial nominal 5-frame bins from a 5-fps acquisition the effective frame rate is 1 fps.

After independently running the pinned upstream, use --flow-pkl /path/to/2WCF_output/pkl and --ofv-parameters /path/to/2WCF_output/parameters.json to check the new outputs. The upstream itself still requires its run-path settings to point to the staged image folder.

Staging only checks TIFF magic plus byte hashes, not full TIFF image validity. It does not confirm the experimental value/shape of the images, camera orientation, actual frame time, calibration, or physical walls. The utility intentionally reports these items as unverified.

## Acceptance gate G0 (not yet passed)

| Item | Status |
|---|---|
| Upstream code, revision, I/O and parameters | Source-inspected and pinned |
| Redistribution permission for copying upstream code | **Not established** |
| Input .tif / .tiff compatibility | Adapter created on branch |
| Nominal time pairing and coordinate conversion | Derived; synthetic tests provided |
| Existing downstream sign/coordinate inconsistency corrected | **Not yet** |
| Experimental source-frame mapping and acquisition metadata | **Not verified** |
| Experimental OFV PKL aligned to real concentration maps | **Not verified** |
| Real independent 2WCF-SVD execution | **Not performed** |
| Final G0 data and scientific acceptance | **Blocked on real-data checks** |

This is not a claim of validated OFV or experimental energy-budget closure. Preserve the upstream as read-only; subsequent changes to either current scientific script must be individually tested and reviewed.
