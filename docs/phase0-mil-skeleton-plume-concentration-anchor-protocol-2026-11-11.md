# Phase 0 — MIL/dendrite-skeleton and liquid-plume-assisted Ga–In attenuation calibration

**Status:** Proposed protocol for scientific acceptance, **not an accepted In mass-fraction measurement**. **Date:** 2026-11-11. **Approvals:** owner approved 2014-03-07 MIL/plume benchmarking, calibrated anchor-method development, physical registration and G0 closure work; separate source-code OFV repair in draft PR #14. This is a reviewable **documentation-only** protocol, not a release of research images.

## 0. Source precedence and case-specific limits

- Notebook method authority: repository \`Mathematica_code/Dendrite & Plume Analysis v25.nb\` (MIL solid segmentation; \`getSkeleton\`, \`getCleanSolidSkeleton\`, \`getSolidSkeletons\`, \`getDendriteGrainMasks\`; masked liquid filtering and K-medoids \`getClusters\`). The older example PDFs actually have **v24 notebook** headers; preserve parameter lineage and treat case-specific overrides as candidates, not 2014-03-07 truth. The original 2023 publication master notebook was **not separately identified/verified** as an independent repository artifact.
- Natalia Shevchenko's \`Concentration_mapping_intermediate.docx\` (available in user's Project files, not committed to this public repo) defines \`P(x,y,t)=-ln[I(x,y,t)/I_0(x,y)]\`, where **both I and I0 are dark-corrected**, the baseline I0 is recorded *before* solidification at nominal homogeneous \`C0=25 wt.% In\`, and the two post-solidification endpoints are coarsened thickness-spanning In-rich dendrites at \`~98.6 wt.% In\` and Ga-rich melt channels at approximately \`5–10 wt.% In\`, supported by an independent liquid gallium cell. The three points appeared approximately linear and underpin a **semi-quantitative** model. The PDF figure rounded the endpoints to 98/5. This source is NOT an instruction to label every darkest pixel as 98.6% or every plume as 5%.
- For **2014-03-07**, the original available collection contains **500** 567×276 *processed/cropped* Bit16 TIFFs (Deflate tag 32946), **418** 763×384 *historical algorithm-generated* binary masks, and **418** source IDs \`600,605,...,2685\`. The exact image↔mask spatial transform and processed-frame↔source IDs are **not accepted**. Notebook reports 37.6 µm/pixel and 1 s exposure, not a verified camera clock. Original 2014-03-07 detector radiographs, beam/flat-field and dark stack, measured pre-cooling reference and actual attenuation anchor \`P\` coordinates **have not been identified** in the six large source archives or these processed images. Thus 2014-03-07 may be a good segmentation benchmark now, but its **absolute chemical calibration must remain blocked** until raw radiometric provenance is recovered. See \`docs/phase0-2014-03-07-mil-plume-calibration-test-plan.md\` and case JSON.

## 1. Explicit data representations: NEVER fit to stretched display luminance

For a source-matched, recorded camera exposure \`I_t(x,y)\`, beam/reference image \`R_t(x,y)\`, and detector dark \`D_t(x,y)\`, consider **two independent radiometric branches**:

- dark corrected: \`J_dark,t=(I_t-D_t)/(R_t-D_t)\`, *only if both corrected numerator and denominator are strictly positive*, with saturation and detector-domain masks also enforced;
- reference only: \`J_no-dark,t=I_t/R_t\`, as an explicit sensitivity/control branch, **not automatically the scientifically preferred method when measured dark current exists**.

The \`R_t\` may be a documented full-stack per-pixel mean only after establishing source correspondence and stability. A historical TIFF labelled \`Averaged\` is not automatically equivalent to original detector means. Explicitly preserve independent branch validity masks and no-dark/dark disagreements; never set negative valid optical density to zero. Distinguish the camera/beam flat-field **R** from the pre-solidification sample composition baseline **J0**.

For each branch, establish a time reference \`J0(x,y)\` from multiple *verified homogeneous all-liquid* frames before cooling/solidification, with valid masks and spatially resolved robust aggregation. Define the **relative attenuation**

\`P_t(x,y)=-ln(J_t(x,y)/J0(x,y))\`.

Thus \`C_In(initial bulk)=25 wt.%\` corresponds to \`P=0\` by definition (subject to independently verified initial composition). Record source frame IDs/timestamps, flat-fields, pixel-domain transformation, baseline time interval and beam/detector drift; repeat relative attenuation separately for both radiometric branches.

The physical transmitted X-ray signal is a **path-integrated** measurement through the cell. A 2D segmentation class does not determine the 3D solid filling fraction or verify a full-thickness dendrite. If solid and liquid overlap along the beam, projected attenuation alone cannot uniquely identify both local chemistry and solid fraction.

## 2. Baseline anchor A0 — nominal initial 25 wt.% In

**A0 = (P0=0,C0=25 wt.% In)** only for **independently verified pre-solidification, homogeneous, all-liquid** sample images. Do not use "first saved Frame_1" if its source index and original cooling onset are not known; for 2014-03-07 the supplied 500 processed crops do NOT currently prove such an initial frame exists.

- Require no MIL-detected solid, steady background (temperature/illumination/absorption checks), no wall/edge masks, spatial homogeneity, and a temporal plateau before cooling. Do not construct a baseline from a bright high-K plume cluster after segregation.
- Select a **temporal block** of reference frames, use robust per-pixel reference \`J0(x,y)\` for normalization, and reserve a disjoint initial block for held-out zero-attentuation validation. Quantify spatial residuals, temporal drift, within-frame dispersion and calibration-preparation uncertainty.
- Differentiate **initial bulk (known 25 wt.%)** from **later far-field/ambient liquid**. The latter has unknown, evolving \`C_bulk(t)\` after solute rejection/transport; use its measured \`P_t\` and the fitted calibration, and characterize \`Delta P_plume-bulk(t)\` without forcing later ambient liquid to 25 wt.%.

## 3. Upper anchor A_s — coarsened indium-rich solid / dendrite

**Candidate source in v25:** temporal MIL solid mask → robust connected solid regions/erosion → \`getSkeleton\`, \`getCleanSolidSkeleton\`, \`getSolidSkeletons\`, \`getDendriteGrainMasks\` and orientation/branch characterization, all with source-frame identity. The v25 skeleton framework is an appropriate **geometrical selector**, not an independent chemistry or thickness measurement.

### Independent candidate constraints
1. Choose late, coarsened, connected dendrites **well inside** the verified solid domain, away from meniscus/walls/overlapping branches and radiographically invalid pixels.
2. Use a distance transform of the accepted binary solid mask and a guard band determined by instrument point-spread width, registration error and skeleton segmentation uncertainty; sample from **thick interior sections around the skeleton**, not the skeleton pixel line alone, extrema, interfaces, tips, branchpoints or the darkest isolated pixel.
3. Prefer extended, spatially stable **high-attenuation interior plateaus** measured on *original unfiltered* \`P_t\` (after correct radiometry), with low local \`|grad P|\`, robust percentiles, and temporal consistency. Positive \`P\` with greater In absorption is a candidate sign check; confirm actual instrument response, not image display polarity.
4. Prefer dendritic morphologies physically compatible with coarsened crystals/side branches oriented **along the X-ray beam** and spanning full Hele–Shaw cell thickness, as required by the original Shevchenko method. A 2D projection or skeleton alone cannot prove full thickness. Require independent experimental geometry, projection plateau, reference filled-cell data or expert adjudication of that condition.
5. Store separate candidate regions from **multiple spatially distinct branches and times**, blocked bootstrap by branch/time, and reject disagreement beyond measured radiometry/PSF uncertainties.

Only approved full-thickness-solid candidates may be assigned \`C_s≈98.6 wt.% In\` with an explicit physical prior and uncertainty. Others remain **unlabelled solid P references** or may constrain a path-length/partial-volume sensitivity model, not unconditional full-solid anchors. The same solid reference should not be blindly used as a liquid-phase Beer–Lambert calibration point if density/phase absorption differs; check an appropriate optical mixture/density model before pooling.

## 4. Lower anchor A_l — verified Ga-rich melt channel, NOT automatically any plume

**Input region:** verified physical liquid mask = cell/detector-valid field, excluding solid mask **dilated by front uncertainty**, walls, field boundaries and saturated/invalid pixels. Use v25 liquid filtering / nonlocal means and \`getClusters\` (\`KMedoids\`) **on a separate image copy**; sample original unfiltered \`P_t\` in accepted cores.

- Sweep \`K={9,12,16,24,32}\` and prefilters \`{none,median,Gaussian,bilateral,nonlocal}\`. Use original v25 sequential prefilter + masked-liquid \`K=9\` as baseline. Compare against an *unmasked high-K negative control* to measure K spent on solid/background.
- Rank each cluster by **median physical unfiltered P**; color palette and K index are not chemical composition. Segment connected coherent liquid structures and, when possible, advect/track them using only source-registered, convention-correct OFV. Prefer cores eroded away from mixing interfaces and unresolved narrow streamers; require spatial plateau, temporal persistence and independent tracking.
- For a candidate **Ga-rich channel or plume core**, compare its attenuation with that of local far-field liquid *at the same time*; require evidence that its attenuation is enriched in Ga rather than affected by temporal beam/detector drift, solid path occlusion, scattering or phase boundary.
- Distinguish the **original method's post-solidification Ga-rich melt channel** (potential endpoint) from **all detected convective plumes**, whose compositions are generally continuous and unknown. The latter are **targets of the calibration**. Do NOT use every low-absorption K-medoid core as \`5 wt.% In\`; this would be circular.
- The approximately \`5–10 wt.% In\` composition label is an **interval with uncertainty**, not an exact 5% target unless justified by independently measured reference such as the liquid-gallium-filled-cell or defensible local phase equilibrium measurements at the actual thermodynamic conditions. If no chemical validation is available, retain \`P_low\` as an optical contrast and **do not fit an absolute composition endpoint**.

Potential automatic sampling geometry: liquid-only components, distance-to-solid/front and wall masks, long-lived lowest-In-candidate attenuation level **cores**, excluding uncertain high-gradient/low-validity pixels. Sample robust \`P\` medians over each connected core and an independent temporal window rather than a single max/min-pixel statistic.

## 5. Three-reference model and acceptance

**Proposed measured objects:** \`A0=(P0≈0,C0=25)\`, \`As=(Psolid,Csolid≈98.6)\`, \`Al=(Pchannel,Cchannel∈[5,10])\`. Each anchor must have: case ID, exact source image and instrument/beam reference SHA-256, source frame/time, coordinate transform, acquisition/run identity, phase, mask version, pixel count, connected ROI IDs, raw \`P\` distribution/percentiles, cluster/filter settings, chemical evidence, effective number of independent regions and uncertainty.

Begin with a **monotonic linear liquid-phase hypothesis**

\`C_In(P)=C0 + beta P\`, \`C0≈25 wt.%\` at \`P=0\`,

and compare against the actual three independently supported anchor distributions using errors-in-variables/robust uncertainty-aware fitting. Do **not** overfit a quadratic to only three nominal endpoints. The original semi-quantitative three-point line is a *hypothesis* for a particular acquisition; a solid endpoint may warrant a separate phase/density attenuation model.

Treat \`Cchannel∈[5,10]\` as interval-censored composition uncertainty. Account for sample correlation by blocking by branch, plume/channel region and time—not thousands of spatially adjacent pixels as independent observations. For true model assessment, reserve separate initial baseline times, selected dendrite branches and candidate channels/plume trajectories as **held-out** regions. Report:
- calibration slope, fitted offset/intercept, uncertainty band and phase/path-length sensitivity;
- anchor residuals and held-out \`wt.%\` errors (only if true chemical labels exist);
- fraction of invalid radiometric pixels and prediction outside physical range;
- sensitivity to reference-only versus dark-corrected radiometry and reference/dark exposure selections;
- sensitivity to MIL parameters, mask boundaries, K and filtering, and to old-v24 versus current-v25 segmentation;
- temporal consistency and beam/pixel thickness issues.

Use the fitted composition field only inside **verified phase-appropriate masks**. Do not silently clip physically implausible \`C_In\` to 0–100%; flag/refuse or document separate display-only clipping.

## 6. 2014-03-07 work breakdown and G0 gates

| Milestone | Implementation | Decision gate |
|---|---|---|
| R1 — image/source lineage | Verify real source index for **each of 500 TIFFs**, 418 masks and 418 IDs; recover original \`Locator\`/ImageTake crop transforms and any resize; inspect original detector-ref and dark availability | Match dimensions and physical pixels **before** applying historical mask on cropped image; neither count nor shape match is sufficient |
| R2 — true temporal MIL | Replicate v25 MIL with same source series, frame/reference/filt parameters; benchmark 2014 empirical parameters without importing v24 2020 overrides as ground truth; annotate held-out masks | Independent human masks, Dice/IoU and boundary/front distance on a **registered** common image domain |
| R3 — dendrite skeleton anchors | Use the v25 morphological/skeleton/grain framework and physical attenuation plateaus on genuine unfiltered P | Full-thickness assumption separately adjudicated; no automatic 98.6 label |
| R4 — masked plume K-medoids | Test v25 K9 sequential filter as baseline; alternate K and prefilters, masked vs unmasked; connected plume/core tracking and liquid P sampling | Ground-truth plume/channel ROIs, temporal stability, correct liquid-only domain; K occupancy/RMSE insufficient |
| R5 — reference/anchor fit | Recover **pre-solidification 25 wt.% frame**, source-matched reference/dark, validated 98.6 and 5–10 composition evidence; fit uncertain linear/phase-aware C(P) | No absolute fitted C for 2014 unless actual raw radiometry and chemical anchors are accepted |
| R6 — source-matched OFV integration | Gate upstream TIFF hashes, image bin membership, \`phase0_time_registration.py\` source times and 2WCF PKL pair centers, crop transforms, accepted physical pixel scale, vector conventions | Only then claim aligned \`C_In(x,y,t)\`, \`u_image(x,y,t)\`, \`v_image(x,y,t)\`; mechanical energy validation later G3/G4 |

**Current scientific admission:** 2014-03-07 is **accepted as a metadata-backed test case for algorithm development**, not yet an accepted chemical calibration or G0 pass. Its provided first processed frame is **not certified** as original homogeneous melt. If the true 2014 original pre-cooling frames and beam/dark data cannot be recovered, use another source-matched experiment that has them for an absolute three-point concentration calibration; continue to use 2014-03-07 for **relative luminance/solid/plume segmentation** once geometry is resolved.

## 7. Reproducibility and review boundaries

- Do not edit/execute the historical v24/v25 notebook wholesale or use its definitions without source-capture and independent Mathematica regression. Preserve the original v25 .nb as code-method authority.
- Store original source-hash manifests, drift/stability diagnosis, sample-mask images, candidate-anchor tables, uncertainty models and class-parameter sweeps privately on authorized X:. Repository docs may include method/provenance and derived numerical summaries without publishing original research images unless permissions are granted.
- Use Library \`/Tools\` active Wolfram Language Engineering, Scientific Validation & Benchmarking, Experimental Automation & Provenance and GitHub Repository Workflow protocols. Separate synthetic acceptance from real source admission.
- Open any candidate algorithm change as a **distinct reviewable PR**; this protocol authorizes no silent modifications of production OFV or energy-balance calculations.
