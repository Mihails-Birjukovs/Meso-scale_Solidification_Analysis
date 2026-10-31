# Agent handoff — Phase 0 OFV data contract and upstream code-use boundary

**Date:** 2026-10-31 (Europe/Riga)  
**Agent ID:** ChatGPT GPT-6 / Coding-Optimization-Docs / Meso-scale-Solidification-OFV  
**Repository:** Mihails-Birjukovs/Meso-scale_Solidification_Analysis  
**Feature branch:** feat/phase0-ofv-contract-2026-10-31  
**Status:** Proposed documentation and standalone Phase-0 checker; **not merged into main** when authored.

## Context and user's approval

After merging PR #1 (mass-fraction density correction C03) the user approved proceeding with Phase 0 from docs/validation-roadmap.md and proposed using a local copy of the external 2WCF-SVD source to allow the assistant to operate independent OFV runs. The upstream repository is **read-only** and current external code must be inspected before any reuse. The user authorizes scientific work with the code, but no public license or explicit redistribution grant was found for a vendored copy.

## What was inspected

- **Target main HEAD:** 3ec766c9be38fed83df3dc44aee77bc4b9ec304e.
- **Upstream:** pienins/Optical-flow-svd-and-fourier-filtering, main commit 27659ae0e0f798189e1fc7c4516453374ad3c9eb (2026-09-22).
- **Upstream source:** 2WCF-SVD_v4_4.py, git blob 52d20820314a1e4283a325dc34e899191bf267b4, author credits Ansis Z / Mihails B.
- Upstream file tree has no README or LICENSE file. Its input accepts only .tiff; default VelocityInversion=-1 multiplies both u and v **after** cv2.calcOpticalFlowFarneback(prev,next).
- Upstream output PKL contains x,y,u,v saved per neighboring image pair, plus parallel WXF and run metadata.
- Target ImagePreprocessWithReference.py exports filtered3D_%05d.tif, and concentration maps Conc_In_%05d.tif. Both scripts still use experiment-specific Windows paths.
- Target VelocimetryRaksturlielumi.py currently flips only v without spatial coordinate transform; known scientific blocker C01. This PR does **not** change that existing script.
- Relevant current Library /Tools instructions actually read for this task: README_FIRST.md, TOOL_ROUTER_v1.0.0.md, GitHub Repository Workflows README + governing protocol v1.0.0 + current addendum v1.3.0, Scientific Validation & Benchmarking README. These are source guidance and are not executable installed skills.

## Changes proposed on this branch

1. Python_code/phase0_contract.py: stdlib-only audit of indexed TIFFs/PKL filenames; exact bin/pair midpoint time calculation; x-right/y-up conversion accounting for upstream inversion; .tif -> .tiff **byte-preserving staging** with SHA-256 integrity; JSON manifest; no pickle execution.
2. tests/test_phase0_contract.py: 11 synthetic/offline tests on timing, coordinates, gaps, duplicate indices, inverted flow and TIFF staging; no experimental data or external 2WCF code.
3. .github/workflows/phase0-contract.yml: standard-library tests under Python 3.11.
4. docs/phase0-ofv-integration.md + docs index link: source identity, scope, limitations, example CLI and G0 gate.
5. This dated **append-only** handoff; prior reports not edited.

## Rights / distribution decision

Do not copy the full upstream source into this **public** solidification repository until authors/license grant explicit redistribution authorization. Public readability and a user preference for convenience do not themselves establish a redistribution license. A separate, locally pinned checkout suffices for scientific evaluation. Future explicit license grant would permit a separately reviewed vendor/submodule approach. No external image archives or measured frames are bundled.

## Unresolved G0 work

- Verify actual raw source indices, reference images, time binning and full-crop geometry with experimental records. The manifest's timestamps are conditional on correct inputs.
- Validate image dimensions and intensity/radiometric references, full raw-to-binned time alignment, actual flow PKL numeric data and x/y component sense.
- Carry through a single coherent pixel-to-physical coordinate transformation into the existing production postprocessor. Do not silently flip v alone.
- Run the pinned real 2WCF-SVD code on staged experimental images in an isolated pinned environment (not done by this PR).
- Gate G0 is **not passed**, and quantitative physics/energy validation must not be claimed from these checks alone.
- Record new tests and real-data evidence before approving any production code changes; earlier C03 density fix was already merged and must be preserved.

## Verification

A GitHub Actions standard-library unit-test run on this branch at commit 548cac0698599329f32e5fa42cba920d47a7014f completed **successfully**: https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis/actions/runs/41220301444 . Subsequent documentation-only commits may have additional CI runs; verify their current status separately. The author did **not** execute the actual upstream on real data.

Continue work via small PRs, preserve calibrated quantitative radiometry, and append a **new** dated handoff for further development rather than editing this one.
