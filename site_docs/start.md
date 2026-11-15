# Getting started

## Choose the workflow

**Historical Mathematica v25 research pipeline:** Use the original notebook in the [public source repository](https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis/blob/main/Mathematica_code/Dendrite%20%26%20Plume%20Analysis%20v25.nb). The original README describes the MATLink/MATLAB bridge and BM3D dependency; these are historical environment requirements, **not** a newly reproduced clean installation. Review notebook initialization and experiment-specific parameters before evaluating actual research data.

**Python extensions:** The original Python scripts and their source-level limitations are documented in the [technical documentation](https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis/blob/main/docs/README.md). The later Phase 0 contrast-mask and morphology candidates are currently in [draft PR #20](https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis/pull/20), and are not guaranteed to exist in the published main branch.

## Read the source before running experimental data

This public repository does **not** distribute the original private Ga–In radiograph archives, registered physical phase ground truth or source-matched OFV results. The 2014-03-07 and 2014-04-04 tests have source-specific checks and cannot be replayed from the public repository alone.

### Minimal review path

1. Read the [methods](methods.md) and the [validation ledger](validation.md).
2. Choose a confirmed sample, source SHA and specific code commit; record acquisition order, detector geometry, flat-field and specimen-baseline roles independently.
3. Use only vetted source data and isolated working copies; do not automatically unpickle untrusted model outputs or promote a test mask into a physical phase label.
4. Run the current available tests and check their exact evidence levels. Synthetic tests can pass while experimental registration remains unverified.
5. Request experimental datasets from the relevant data owners; public source-code availability does not imply public distribution rights for measurements.

For reproducible software fixes, work on an isolated branch and submit a reviewed PR. Original notebook outputs and historic processing decisions should remain archived.
