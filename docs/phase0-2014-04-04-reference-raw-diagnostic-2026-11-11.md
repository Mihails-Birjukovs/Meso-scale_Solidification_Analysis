# 2014-04-04 raw-reference pixel and optical-contrast preflight

**Date:** 2026-11-11. **Scientific status:** verified raw TIFF decoding and descriptive reference-only contrast; no homogeneous-liquid 25 wt.% anchor, absolute concentration or G0 acceptance.

## Source and reproducibility

- Private source: X:\AI-Lab-Test\Solidification_OFV\raw_archives\2014-04-04.7z, 1,507,471,570 bytes, SHA256 77fac9a38a9cdaa41ee5ec9c9562acb7149ee1cee8f0246a80c2b267928f2510.
- Inventory: X:\AI-Lab-Test\Solidification_OFV\analysis_outputs\phase0_2014-04-04_archive_admission_2026-11-11\inventory_with_frames.json; SHA256 4481EE856A00B28C480D669634765A7AA596AC9C4B9FA72C86EA22968845DF78.
- Raw-reference report in same private folder: reference_probe_admitted_crc.json; SHA256 1CA9B17F74BD28B56B46452997A9BFA2318132A77713C642E081C0F728117615.
- Per-frame report in same folder: reference_probe_timeseries_crc.csv; SHA256 74525292A9349B69E9947FC3A5D36EAF3F845ED597D1151A2EBA6B12057A5BA1.
- The module Python_code/phase0_2014_04_04_reference_probe.py accepts private extracted paths and the source-inventory JSON. It refuses replacement of existing output. All 111 reference TIFFs and six selected experiment/end TIFFs passed extracted-byte CRC32 and size comparison against the inventory.
- Python 3.10 native workstation: NumPy 1.26.4, tifffile 2022.10.10, Pillow 9.0.1. First/middle/last reference images agree exactly between tifffile and Pillow. 16/16 synthetic tests passed (10 archive, six scientific-image). Python 3.14 without scientific dependencies: 10 passed, six SKIPPED; do not label these six as CI-tested.

## Detector signal evidence

- All 111 original reference images decode as 426 rows × 761 columns, uint16, grayscale, uncompressed TIFF (compression=1); the six selected original experimental images share those dimensions and sample type.
- Of detector pixels, 2.11576% reached 65535 at least once in the reference time series. 97.88424% were positive and nonsaturated in every reference frame. This is a candidate detector-validity criterion only, not a sample/liquid/solid mask.
- Across nonsaturated reference pixels, the per-frame global median ratio (last/first) was 0.99935652 (−0.06435%) and its largest absolute departure from the first frame was 0.10725%. Median per-pixel temporal MAD was 309 detector counts (p05 243, p95 376). These are descriptive stability statistics; they do not certify homogeneous liquid or beam stability.
- Reference train/test split: first 80 frames for provisional pixelwise temporal-median I0, final 31 held out. Median absolute held-out frame median of negative-log raw-count ratio was 0.00030858; p95 0.00050419.
- Sample median reference-only negative-log contrasts (unfiltered detector pixels, excluding reference/experimental saturation and nonpositive counts): 10:25:47.069 main 0.009018; 10:41:05.056 main 0.009349; 10:41:09.416 main 0.009475; 11:18:23.600 main 0.024591; 11:21:20.997 end 0.049971; 11:26:18.009 end 0.048847. These are NOT In mass fractions and mix wall/sample/beam variation.

## Timebase and science gates

- Source archive: 111 reference TIFF, 3,148 main TIFF and 298 end TIFF. Main contains three filename-based discontinuities of 4.360, 4.359 and 3.813 seconds. Main-to-end gap is 177.397 seconds. Filenames are clock candidates, not verified camera acquisition times. No OFV integration across missing frames by assumed uniform spacing.
- Verify whether Reference is a homogeneous pre-solidification Ga–25 wt.% In sample or another reference preparation; distinguish the sample baseline from detector beam flat-field. Seek measured dark and acquisition/exposure metadata. Do not fabricate measured dark or absolute calibrated concentration.
- Identify physically valid chamber/liquid/solid boundaries, perform source-faithful MIL and plume segmentation and independent annotations. Only then sample full-thickness In-rich dendrites, independently supported Ga-rich channels and homogeneous initial liquid for conditional 98.6/5–10/25 wt.% anchors.
- The 2014-03-07 processed-image/mask-registration case remains separate. This new diagnostic neither merges draft PR #14/#15 nor closes G0.

**Mutation boundary:** original source archive and notebook unchanged; no research TIFF pixels published in GitHub.
