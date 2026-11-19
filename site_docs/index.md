<section class="inm-hero">
<p class="inm-eyebrow">Scientific software · experimental radiography · reproducible methods</p>
<h1>Meso-scale Solidification Analysis</h1>
<p>Image processing, dendritic morphology, liquid-channel and plume analysis, and research-stage optical-flow diagnostics for directionally solidifying metal alloys.</p>
<div class="inm-actions"><a href="start/" class="inm-action-primary">Explore the workflow</a><a href="methods/" class="inm-action">View segmentation methods</a><a href="validation/" class="inm-action">Review validation status</a></div>
</section>

<div class="inm-identity"><div><strong>Research context</strong><p>Institute of Numerical Modelling, University of Latvia, with research contributions from HZDR collaborators. See the published 2023 paper for the original authorship and method.</p></div><div><strong>Scientific evidence status</strong><p>Original Mathematica analysis is publicly available. The newest 2014-04-04 segmentation, morphology and flow-validation work is research-stage and partly in draft pull requests.</p></div></div>

## What the project covers

The historical published method reconstructs solid and liquid domains, morphological dendrite structure, solidification fronts, liquid channels/cavities and solutal convection plumes. Later development adds independently tracked calibration, data provenance, reference correction, optical flow, field kinematics and physical-consistency tests.

The contemporary experiments are **not** all implemented in the published method. In particular, a simple Gaussian-filtered signed-contrast candidate mask is **not** the original dynamic mean inverse luminance (MIL) segmentation; our provisional morphological envelope and proposed temporal component graph remain distinct from both.

## Follow the evidence

- [Full current-code inventory](current-code.md) — historical source-method lineage, Python and Mathematica implementation details, limits and caveats.
- [Full scientific methods and physical model](scientific-methods.md) — governing assumptions, calibrated-versus-proposed terms, numbered equations and uncertainty boundaries.
- [Architecture and source code](architecture.md) — what is in the current public main branch and what is still in PRs.
- [MIL and signed-contrast segmentation](methods.md) — algorithmic distinctions and current gate parameters.
- [Spatial/temporal plume analysis](temporal-model.md) — current spatial experiment and approved T1 research plan.
- [Evidence and validation](validation.md) — exact sample evidence, limitations, held-out experimental gates.
- [Research and credits](research.md) — primary publication, collaborators, rights and data boundaries.

**Publication status:** The documentation website is deployed through GitHub Pages (GitHub Actions) and its eight public routes plus CSS were checked on 2026-11-15. This is **not** a declaration that experimental plume segmentation, physical phase labeling, composition mapping or optical-flow models have been scientifically validated. Original radiographs, private workstation paths, laboratory credentials and other unapproved institutional artwork remain excluded. The INM header, favicon and footer marks are reused by owner request, separately from the project's software license.
