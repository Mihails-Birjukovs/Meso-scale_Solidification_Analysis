A Wolfram Mathematica image processing code for automated analysis of metal alloy solidification in Hele-Shaw cells, originally designed for dynamic X-ray imaging applications.  

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
- Improving performance by offloading some image filtering tasks to the GPU (CPU-only version will be kept as separate)  

The underlying methodology, implementation and application examples are found in [ARXIV PREPRINT ID].  

ACHTUNG: this Mathematica code uses MATLink  
(MATLink hyperlink)  
and couples the code to the MATLAB engine to use this BM3D implementation:  
(BM3D link)  
Both MATLink and MATLAB are currently hard requirements.