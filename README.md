A Wolfram Mathematica image processing code for automated analysis of metal alloy solidification in Hele-Shaw cells, originally designed for dynamic X-ray imaging applications.  

ACHTUNG: this Mathematica code uses MATLink  
http://matlink.org/  
and couples the code to the MATLAB engine to use this BM3D implementation (currently v3.0.9):  
https://webpages.tuni.fi/foi/GCF-BM3D/index.html#ref_software  
Both MATLink and MATLAB are currently hard requirements.  

Current functionality:  
- Liquid/solid domain segmentation  
- Liquid cavity & channel (chimney) detection  
- Solidification front derivation  
- Solute concentration measurements above the solidification front and in the liquid domain  
- Deriving the dynamics of the solidification front shape and its motion  
- Multi-level segmentation of convective plumes  
- Dendrite skeleton detection in the solid domain & orientation analysis  
- Decomposotion of the solidified structures into grains by orientation & distance  

Features under development:  
- Primary dendrite spacing measurements  
- Deriving the local thickness of the solidified structures  
- Optical flow velocimetry within the liquid domain
- Improving performance by offloading some image filtering tasks to a GPU (a CPU-only version will be kept as a separate branch)  

The underlying methodology, implementation and application examples are found in:  
https://link.springer.com/article/10.1007/s00348-023-03671-2 (paper + supplementary material .pdf)

---

## Technical documentation (2026-10-22)

The original description above summarizes the **published Mathematica solidification-analysis pipeline** and historical software prerequisites. For the current Python research extension, consult the [complete technical documentation](docs/README.md):

- [Architecture and operating contract](docs/architecture-and-workflow.md)
- [Existing source-code inventory and methods lineage](docs/current-code.md)
- [Scientific models and equations](docs/scientific-methods.md)
- [Confirmed issues and uncertainty register](docs/known-issues.md)
- [Approved validation plan](docs/validation-roadmap.md)
- [Publications, calibration provenance and external data](docs/references-data.md)

**Current development focus:** `Python_code/ImagePreprocessWithReference.py` and `Python_code/VelocimetryRaksturlielumi.py`. The original Mathematica notebooks remain research/methodological references. The independent [2WCF-SVD optical-flow repository](https://github.com/pienins/Optical-flow-svd-and-fourier-filtering) is a **read-only upstream dependency** and is not to be modified here.

The documentation separates **current implemented behavior** from **proposed and user-approved scientific models**. No claim is made that the experimental Ga–In energy budget has been validated or closed. For research-agent continuity see the [append-only handoff protocol](Handoff_file_exchange/README_for_agents.md) and [22 October 2026 comprehensive handoff](Handoff_file_exchange/2026-10-22_gpt6_full-chat_scientific-model-and-documentation-handoff.md).
