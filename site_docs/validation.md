# Validation, scientific limits and open gates

## Evidence levels are not interchangeable

| Evidence | Current status |
|---|---|
| Original public Mathematica source and paper | Available; published methods described in the 2023 article |
| Original 2014-04-04 archived source inventory and reference role | SHA/CRC source verification and detector flat-field role established |
| Pilot contrast masks on selected original TIFF frames | Source-checked, synthetic tests and sensitivity sweeps; research-only |
| Provisional front and discarded magenta components | **Experiment-owner visually accepted for shown examples**, not independent pixelwise truth |
| Full original MIL dynamic-threshold replay for 2014-04-04 | Incomplete: historical native probe is not full pipeline equivalence |
| Stage T1 dense source and associations | Approved next development, not yet validated |
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
