(* Native Wolfram Kernel 12.1.1 read-only v25 MIL-method sample probe.
   Use: wolframscript -file this_file.wls config.json
   The configuration supplies absolute source TIFF paths and a prepared float32
   flat-field R TIFF. NEVER Get/Evaluate the original notebook as code.
   Source method: Mathematica_code/Dendrite & Plume Analysis v25.nb
   verified Git blob SHA b13ef6adda22405d89680e3ebe5da50e6f40d297.
   This is NOT the historical case-specific segmentation pipeline. *)
If[Length[$ScriptCommandLine]<2,Print["PASS_CONFIG_JSON"];Exit[2]];
configPath=Last[$ScriptCommandLine];
If[!FileExistsQ[configPath],Print["CONFIG_MISSING"];Exit[2]];
config=Quiet@Check[Import[configPath,"RawJSON"],$Failed];
If[!AssociationQ[config],Print["CONFIG_NOT_ASSOCIATION"];Exit[2]];
refPath=Lookup[config,"flat_field_R_tiff",Missing["NotFound"]];
fileNames=Lookup[config,"sample_source_tiffs",Missing["NotFound"]];
out=Lookup[config,"output_json",Missing["NotFound"]];
gaussianKernelScale=Lookup[config,"gaussian_kernel_scale",0];
If[!StringQ[refPath]||!FileExistsQ[refPath]||
   !ListQ[fileNames]||Length[fileNames]<1||
   !VectorQ[fileNames,StringQ]||!And@@(FileExistsQ/@fileNames)||
   !StringQ[out]||FileExistsQ[out]||
   !NumericQ[gaussianKernelScale]||gaussianKernelScale<0,
  Print["INVALID_CONFIG_OR_OUTPUT_EXISTS"];Exit[2]];
referenceFrame=Import[refPath];
If[!ImageQ[referenceFrame],Print["BAD_REFERENCE_IMAGE"];Exit[3]];
dims=ImageDimensions[referenceFrame];
flatPixels=Flatten@ImageData[referenceFrame,"Real32"];
If[Min[flatPixels]<=0||!VectorQ[flatPixels,NumericQ],
 Print["NONPOSITIVE_FLAT_FIELD"];Exit[3]];
(* Match v25 method form exactly; only the prepared case-specific R input differs
   from original unrecovered evaluated notebook referenceFrame. *)
flatFieldCorrect[image_,flatField_]:=ImageMultiply[image,flatField^-1];
getMILseries[image_]:=Mean@ColorNegate@ImageAdjust@GaussianFilter[
 flatFieldCorrect[image,referenceFrame],gaussianKernelScale];
rows={};
Do[
 im=Quiet@Check[Import[file],$Failed];
 If[!ImageQ[im]||ImageDimensions[im]=!=dims,
  Print["BAD_SOURCE_IMAGE_OR_GEOMETRY ",file];Exit[4]];
 value=Quiet@Check[getMILseries[im],$Failed];
 If[!NumericQ[value]||!TrueQ[0<=value<=1],
  Print["BAD_NUMERIC_MIL ",file];Exit[4]];
 AppendTo[rows,<|"file_basename"->FileNameTake[file],
   "native_v25_method_MIL"->N[value,12]|>];
 Print[FileNameTake[file]," NativeMIL=",N[value,8]];
 ,{file,fileNames}];
report=<|
 "schema"->"ga-in-native-v25-method-mil-sample/v1",
 "status"->"NATIVE_METHOD_FORM_SAMPLE_NOT_HISTORICAL_REPLAY_NOT_SEGMENTATION_ACCEPTANCE",
 "source_notebook_git_blob_sha"->"b13ef6adda22405d89680e3ebe5da50e6f40d297",
 "wolfram_version"->$Version,
 "reference_role"->"owner_confirmed_flat_field_correction",
 "flat_field_reference_input"->FileNameTake[refPath],
 "gaussian_kernel_scale"->gaussianKernelScale,
 "source_image_dims_wh"->dims,
 "sample_count"->Length[rows],
 "original_case_preprocessing_or_ROI_verified"->False,
 "historical_case_MIL_thresholds_verified"->False,
 "dark_correction_verified"->False,
 "composition_calibration_admitted"->False,
 "results"->rows|>;
Quiet@Check[Export[out,report,"JSON"],$Failed];
If[!FileExistsQ[out],Print["REPORT_EXPORT_FAILED"];Exit[5]];
Print["NATIVE_METHOD_SAMPLES_DONE ",Length[rows]];
