# Architecture and scientific source authority

## Separate historical, production and research stages

| Layer | Source authority | Current interpretation |
|---|---|---|
| Published Mathematica image analysis | Original v25 notebook plus 2023 publication | Historical MIL, segment/morphology and plume pipeline; do not silently modify equations |
| Active Python image/OFV postprocessing | Main-branch Python files | Implements radiometry and OFV calculations with dataset-specific assumptions; physical G0 still open |
| Phase 0 admission and calibration | Main-branch data provenance modules, documentation and tests | Original TIFF inventories, clock and reference-role evidence; not automatic quantitative composition admission |
| Expanded signed-contrast candidate masks | Draft PR #20 | Threshold-sensitivity review and model-owner feedback, NOT original MIL |
| Morphology-derived front and whole-component negative gate | Draft PR #20 | Three reviewed frames have visually accepted provisional front and excluded artifacts; not pixel ground truth |
| Spatial-temporal component graph T1 | Approved research design | Proposed next implementation and independent ablation; not validated experimental output |
| Component CRF T2 | Optional backup research design | Neither trained nor calibrated |

## Major interfaces

Original x-ray radiographs and reference recordings enter the image-processing branch. Detector reference images are **flat fields**, while an initial homogeneous specimen reference is a different acquisition concept. Signed contrast and candidate segmentation operate in original detector geometry before any physical coordinate transformation.

An external optical-flow method, [2WCF-SVD](https://github.com/pienins/Optical-flow-svd-and-fourier-filtering), remains an independently owned, read-only upstream. Its outputs are not automatically time-aligned or spatially registered against the source radiographs; the physical field integration gate must confirm these mappings.

## Provenance and privacy

Raw TIFFs, radiometric/thermal experimental metadata, internal X: workspace archives, true phase annotations and unapproved research imagery are **excluded from this public site**. The public GitHub project is the software/source authority; its live PRs, CI runs and data-rights status are distinct.

See the [complete code inventory](current-code.md), [scientific methods and physical model](scientific-methods.md), and [open technical issues](https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis/issues). Both documents are now rendered directly within this website, with links to their authoritative GitHub Markdown originals.
