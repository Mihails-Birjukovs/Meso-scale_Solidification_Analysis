# Validation, scientific limits and open gates

## Evidence levels are not interchangeable

| Evidence | Current status |
|---|---|
| Original public Mathematica source and paper | Available; published methods described in the 2023 article |
| Original 2014-04-04 archived source inventory and reference role | SHA/CRC source verification and detector flat-field role established |
| Pilot contrast masks on selected original TIFF frames | Source-checked, synthetic tests and sensitivity sweeps; research-only |
| Provisional front and discarded magenta components | **Experiment-owner visually accepted for shown examples**, not independent pixelwise truth |
| Full original MIL dynamic-threshold replay for 2014-04-04 | Incomplete: historical native probe is not full pipeline equivalence |
| Stage T1 dense source and associations | Source-CRC executed on 858 frames; still no independent physical-plume ground truth |
| Stage T2 calibrated CRF | Not implemented; conditional design |
| True chamber phase annotations and verified initial liquid baseline | Open |
| Temperature/gradient chronology | Requested from experiment collaborators; not reported here as received |
| Absolute indium mass-fraction map, experimental energy closure | Not admitted |

## Non-negotiable tests

Temporal models must preserve motion-consistent plume-like extensions and reject source-stationary artifacts without falsely deleting short-lived events. Test genuine plume splitting/merging, complete low-contrast phases, missing frames, frame-clock gaps, source registration drift, spatial wall/corner artifacts and source-matched false-positive controls.

Fixed geometry, code/commit SHA, original TIFF member checksums, data rights, public-vs-private provenance and parameter grids are prerequisites. Compare competing variants on identical source data, with held-out time blocks and independent physical phase annotations before reporting precision, recall or statistical calibration.

The existing negative component gate is **not** a validated channel-to-bulk-liquid connectivity test. In the current implementation, ≥10 pixels overlapping a provisional below-front zone retains a whole negative component.

## External dependencies and OFV

Source-relative frame timing is not instrument-certified. Upstream optical-flow vectors and concentration fields must pass source-pair, crop, physical axes, timestamp and valid-domain registration before physics-level validation. Synthetic right/up and rotation tests cannot alone prove real flow recovery or mechanical-energy closure.

For exact reports consult the [current technical validation roadmap](https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis/blob/main/docs/validation-roadmap.md) and [Phase 0 integration record](https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis/blob/main/docs/phase0-final-integration-2026-11-01.md).

## Candidate T1 evidence (draft PR #22, not merged)

Source-linked original 2014-04-04 replay reached 858 frames, 9,397 negative candidate components and 20,738 possible temporal edges. Native 36/36 synthetic tests passed across T1 association, source-pixel shape, channel path and the bounded CRF toy model. The morphology-only/temporal-only/strict-combination ablation found important contradictory candidate subsets and is documented in [experimental PR #22](https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis/pull/22). **Neither a temporal association nor a traversable path through weak/strong optical candidate masks is verified actual fluid/plume physics.** The original user-reviewed morphology outputs remain unchanged.
