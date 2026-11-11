# %%
import os
import glob
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tifffile import imread
from scipy.ndimage import zoom
from scipy.interpolate import griddata
from scipy.spatial import cKDTree
import json # Lai nolasitu parametru prieks arrowdensity un saprastu X, Y režģi
# from scipy.interpolate import griddata #griddata: interpolē (aprēķina) vērtības nezināmos punktos, 
# balstoties uz zināmiem izkaisītiem (x, y, vērtība) datu punktiem — 
# šeit izmantots, lai aizpildītu ātruma lauka (u, v) "caurumus" 
# pilnajā (X, Y) režģī, kur PIV/flow algoritms nav devis datus
import sys # To exit from the loop and stop work
import warnings # Paslēpj warning
warnings.filterwarnings("ignore", message="numpy.core.numeric is deprecated")
import Divergence_Free_Interpolant as dfi
from ofv_coordinate_conventions import (
    require_inversion, forward_image_components,
    physical_vorticity_from_image_derivatives,
)

# %% ====================================================================================
# Input:
# pkl files
# FLOW_FOLDER = r"C:\Users\Lenovo\OneDrive - University of Latvia\Desktop\Maģistra darbs\Solidification_image_analysis_code\KodaaIeguutieRaksturlielumi\20260624PKLEnhancedKLD\pkl"
FLOW_FOLDER = r"C:\Users\Lenovo\OneDrive - University of Latvia\Desktop\Maģistra darbs\Solidification_image_analysis_code\KodaaIeguutieRaksturlielumi\20260915PKL\PKL20260915\pkl"
# tiff files
# Concentration field calculated from g_downsampled
CONC_FOLDER = r"C:\Users\Lenovo\OneDrive - University of Latvia\Desktop\Maģistra darbs\Solidification_image_analysis_code\Pre-processing\Example_input_output\Output\2011-09-09-Experiment-1\Conc_In\20261110"
# IMAGE_FOLDER = r"C:\Users\Lenovo\OneDrive - University of Latvia\Desktop\Maģistra darbs\Solidification_image_analysis_code\KodaaIeguutieRaksturlielumi\20260624Cropped\ImagesRun1"
# REFFERENCE_IMAGE_FOLDER = r"C:\Users\Lenovo\OneDrive - University of Latvia\Desktop\Maģistra darbs\Solidification_image_analysis_code\KodaaIeguutieRaksturlielumi\20260624Cropped\ImagesReferenceRun1"
# g_Filtred_FOLDER = r"C:\Users\Lenovo\OneDrive - University of Latvia\Desktop\Maģistra darbs\Solidification_image_analysis_code\Pre-processing\Example_input_output\Output\2011-09-09-Experiment-1\gFiltered\20260825_Nr1"
# FILTRED_IMAGE_FOLDER = r"C:\Users\Lenovo\OneDrive - University of Latvia\Desktop\Maģistra darbs\Solidification_image_analysis_code\KodaaIeguutieRaksturlielumi\20260624Filtered\20260624_4 Downsampled ImagesRun1_20260624_v3_3D_filtered_enhanced_KLD_v2_Run1"

# Base, where we will generate our subfolders
BASE_OUTPUT_FOLDER = r"C:\Users\Lenovo\OneDrive - University of Latvia\Desktop\Maģistra darbs\Solidification_image_analysis_code\KodaaIeguutieRaksturlielumi"
# ============================================================
# For user: name of the folder he wants to create.
atbilde = input("Do you want to create folders? (yes/no): ").strip().lower()

if atbilde == "yes":
    run_name = input("Inert name of the folder (here will be our results): ").strip()
    if run_name == "":
        run_name = "run_without_name"
     
    OUTPUT_FOLDER = os.path.join(BASE_OUTPUT_FOLDER, run_name)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # Subfolders:
    MASK_CHECK_FOLDER = os.path.join(OUTPUT_FOLDER, "Missing_mask_checks")
    os.makedirs(MASK_CHECK_FOLDER, exist_ok=True)
    NPY_FOLDER = os.path.join(OUTPUT_FOLDER, "NPY_arrays")
    os.makedirs(NPY_FOLDER, exist_ok=True) # here will be saved data for all plots
    PLOTS_FOLDER = os.path.join(OUTPUT_FOLDER, "Plots")
    os.makedirs(PLOTS_FOLDER, exist_ok=True)
    # subsubfolder in PLOTS_FOLDER
    WEIGHT_FRACTION_FOLDER = os.path.join(PLOTS_FOLDER, "Weight_fraction_of_gallium")
    os.makedirs(WEIGHT_FRACTION_FOLDER, exist_ok=True)
    # G_FOLDER = os.path.join(PLOTS_FOLDER, "Optical_density_g")
    # os.makedirs(G_FOLDER, exist_ok=True)

    # Katram lauka veidam sava apakšmape plotu iekšā
    FIELD_NAMES = ["speed", "vorticity", "enstrophy_field", "dissipation",
               "kinetic_energy", "density", "viscosity", "gallium_fraction"]
    for name in FIELD_NAMES:
        os.makedirs(os.path.join(PLOTS_FOLDER, name), exist_ok=True)
    print(f"Results are saved here: {OUTPUT_FOLDER}")
    
elif atbilde == "no":
    print("Program stopped. Files will not be created.")
    sys.exit()
else:
    print("Invalid input. Program terminated.")
    sys.exit()
    
# %% ============================================================
# Physical calibration:
downsampling_factor = 4 # For refference image downsampling.
delta_x = 17.5e-6 * downsampling_factor # pixel size in meters *4 because downsampled images
bin_factor = 5 # How many frames are binned
frame_rate = 5  # frames per secound
delta_t = (1 / frame_rate) * bin_factor  # seconds
# Explicit interpolation method. Linear must pass full-domain finite coverage.
INTERPOLATION_METHOD = "rbf"  # alternatives: "rbf", "linear"
if INTERPOLATION_METHOD not in {"rbf", "linear"}:
    raise ValueError("INTERPOLATION_METHOD must be rbf or linear")

# ============================================================
# Material parameters:
# sample thickness [m]
d = 0.15e-3
# densities [kg/m^3]
rho_gallium = 5904
rho_indium = 7310
# viscosities [Pa*s]
mu_gallium = 1.7e-3
mu_indium = 1.3e-3
# x-ray attenuation coefficients [1/m]
# zeta_gallium = 33.83 # Photon energy 0.1 Mev
# zeta_indium = 244.1 # 
# zeta_gallium = 902.13 # Photon energy 0.03 MeV
# zeta_indium = 7324.62 # 
zeta_gallium = 7563.024 # Photon energy 30 keV
zeta_indium = 28867.19 

# ArrowDensityStep is in the parameters.json file.
params_path = os.path.join(os.path.dirname(FLOW_FOLDER), "parameters.json")
with open(params_path) as f:
    params = json.load(f)
arrow_step = params["ArrowDensityStep"]
velocity_inversion = require_inversion(params)
print("VelocityInversion:", velocity_inversion)
print("ArrowDensityStep:", arrow_step)

# %% ============================================================
# Load tiff and pkl files
# tiff_image_files = sorted(glob.glob(os.path.join(IMAGE_FOLDER, "*.tiff")),
    # key=lambda x: int(os.path.basename(x).split('_')[1].split('.')[0]))

# for f in tiff_image_files[:10]:
    # print(os.path.basename(f))
    
# if len(tiff_image_files) == 0:
    # raise RuntimeError("No image tiff files found.")
    
conc_files = sorted(glob.glob(os.path.join(CONC_FOLDER, "*.tif")),
    key=lambda x: int(os.path.basename(x).split('_')[2].split('.')[0]))

if len(conc_files) == 0:
    raise RuntimeError("No concentration TIFF files found.")

print("Concentration files:", len(conc_files))

pkl_files  = sorted(glob.glob(os.path.join(FLOW_FOLDER, "*.pkl")))
if len(pkl_files) == 0:
    raise RuntimeError("No pkl files found.")

# The count of images and pkl files differ by 1, so we will take len(pkl_files)
n_frames = min(len(conc_files), len(pkl_files))
print("Used picture count: ", n_frames)
# Cik kadrus apstrādāt:
N_FRAMES_TO_PROCESS = 5  # None = apstrādāt visus pieejamos kadrus

if N_FRAMES_TO_PROCESS is not None:
    n_frames = min(N_FRAMES_TO_PROCESS, len(conc_files), len(pkl_files))

print("Frames to process:", n_frames)


# %% ============================================================
# Check pkl file
with open(pkl_files[0], "rb") as f:
    data_test = pickle.load(f)
print("Pkl data key values:", data_test.keys())

# Izvēlas līdz piemēram 5 kadriem no TIEŠI apstrādājamajiem kadriem
check_frames = set(np.linspace(0, n_frames - 1, min(5, n_frames), dtype=int))
print("Frames with missing data mask:", (np.array(sorted(check_frames)) + 1).tolist())

summary = [] # Here we save the info

# to check dissipation equation \epsilon(t)...
kinetic_energy_total = []
dissipation_total = []
time_values = []

# %% Check concentration and velocity compatibility
# ============================================================

# First concentration image
C_test = imread(conc_files[0])

# First velocity field
with open(pkl_files[0], "rb") as f:
    flow_test = pickle.load(f)

x_test = np.asarray(flow_test["x"])
y_test = np.asarray(flow_test["y"])

h, w = C_test.shape

print("\n================================")
print("DATA COMPATIBILITY CHECK")
print("================================")

print("First concentration file:", os.path.basename(conc_files[0]))
print("First velocity file:", os.path.basename(pkl_files[0]))

print("\nConcentration image shape:", C_test.shape)
print("Image width:", w)
print("Image height:", h)

print("\nVelocity coordinates:")
print("X min:", np.min(x_test))
print("X max:", np.max(x_test))
print("Y min:", np.min(y_test))
print("Y max:", np.max(y_test))

print("\nVelocity vectors:", len(x_test))

# Check coordinate limits
inside = (
    (x_test >= 0) & (x_test < w) &
    (y_test >= 0) & (y_test < h)
)

print("Vectors inside image (%):", np.mean(inside) * 100)
# %% ============================================================
# MAIN LOOP
# ============================================================
for frame_index in range(n_frames): 
    pkl_path = pkl_files[frame_index]

    # Load pre-calculated indium concentration field
    C_in_percent = imread(conc_files[frame_index]).astype(np.float32)
 
    print(f"Frame {frame_index + 1}: "
    f"C_In min={C_in_percent.min():.3f}%, "
    f"max={C_in_percent.max():.3f}%")
    
    
    # Indium and gallium mass fractions [-]
    w_indium = C_in_percent / 100.0
    w_gallium = 1.0 - w_indium
    # alpha_indium = C_in_percent / 100.0
    # alpha_gallium = 1.0 - alpha_indium

    # Pārbaude:
    plt.figure()
    plt.hist(w_indium.flatten(), bins=100)
    plt.axvline(0, color='r', linestyle='--')
    plt.axvline(1, color='r', linestyle='--')
    plt.title("Indium mass fraction before clipping")
    plt.show()
    
    w_gallium = np.clip(w_gallium, 0, 1)
    w_indium = 1 - w_gallium
    
    # Šo saglabās apakšmapē.
    plt.figure(figsize=(6,5))
    plt.imshow(w_gallium, origin="upper", aspect="auto", vmin=0, vmax=1)
    plt.colorbar(label="Gallium mass fraction $w_{\mathrm{Ga}}$")
    plt.title(f"Gallium mass fraction | frame {frame_index}")
    plt.tight_layout()
    plt.savefig(os.path.join(WEIGHT_FRACTION_FOLDER, f"Gallium mass fraction_{frame_index:05d}.png"))
    plt.close()

    # Reconstruction of density and viscosity
    
    # Mixture density [kg/m³]
    rho = 1.0 / (w_gallium / rho_gallium + w_indium / rho_indium)

    mu = (w_gallium * mu_gallium + w_indium * mu_indium)

    # ========================================================
    # Load velocity field
    with open(pkl_path, "rb") as f:
        data = pickle.load(f)

    x = data["x"]
    y = data["y"]
    # print(x)
    # print(y)
    u_pix = data["u"]
    v_pix = data["v"]
    # print(u_pix)
    # print(v_pix)
    
    # ========================================================
    # Convert to physical velocity
    # Both saved 2WCF components have the upstream VelocityInversion.
    # Preserve x-right/y-down image basis through image-grid interpolation.
    u, v = forward_image_components(
        np.asarray(u_pix, dtype=float), np.asarray(v_pix, dtype=float),
        inversion=velocity_inversion, m_per_pixel=delta_x, pair_dt_s=delta_t,
    )

    # ========================================================
    # Grid reconstruction (grid + interpolation)
    h, w = C_in_percent.shape  # dimensions of the image

    x_full_1d = np.arange(arrow_step // 2, w, arrow_step)
    y_full_1d = np.arange(arrow_step // 2, h, arrow_step)  
    # print("x coord ", x_full_1d)
    # print("y coord ", y_full_1d)
    
    nx = len(x_full_1d)
    ny = len(y_full_1d)
    X, Y = np.meshgrid(x_full_1d, y_full_1d)  # shape (ny, nx)

# ============================================================
# Grid indices and missing-data mask
# ============================================================

    # ChangeCoordinates to nearest grids index.
    x_idx = np.rint((np.asarray(x) - x_full_1d[0]) / arrow_step).astype(int)

    y_idx = np.rint((np.asarray(y) - y_full_1d[0]) / arrow_step).astype(int)

    # Pārbaudām, vai koordinātas atrodas režģa robežās.
    inside_grid = ((x_idx >= 0) & (x_idx < nx) & (y_idx >= 0) & (y_idx < ny))

    # Atsevišķi izveidojam reāli novēroto punktu masku.
    mask_present = np.zeros((ny, nx), dtype=bool)
    mask_present[y_idx[inside_grid], x_idx[inside_grid]] = True
    mask_missing = ~mask_present

    print(f"Grid: {ny} x {nx}; "
        f"measured grid points: {mask_present.sum()}; "
        f"missing grid points: {mask_missing.sum()}; "
        f"outside-grid measurements: {(~inside_grid).sum()}")

    # ========================================================
    # Visualization of missing point mask.
    # ========================================================
    if frame_index in check_frames:
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        axes[0].imshow(C_in_percent, cmap='gray')
        axes[0].quiver(x, y, u, v, color="lime")
        axes[0].set_title(f"Image frame {frame_index + 1}")
        axes[0].axis('off')

        # extent = [left, right, bottom, top]
        axes[1].imshow(mask_present, extent = [0, w, h, 0], cmap='gray', aspect='equal', vmin=0, vmax=1)
        axes[1].scatter(x, y, s=6, c='red', alpha = 0.5, label='real data points')
        axes[1].set_title(f"White = there is data , black = missing data | missing {mask_missing.sum()}/{ny*nx}")
        axes[1].legend(loc='upper right', fontsize=7)
        # axes[1].invert_yaxis()

        plt.tight_layout()
        plt.savefig(os.path.join(MASK_CHECK_FOLDER, f"missing_mask_check_{frame_index:05d}.png"), dpi=150)
        plt.close(fig)
        print(f"Frame {frame_index + 1}: grid size: {ny}x{nx}={ny*nx}; data points: {mask_present.sum()}; missing data points: {mask_missing.sum()}")
        
        
   
    # ============================================================
    # VELOCITY FIELD INTERPOLATION AND DIAGNOSTICS
    # ============================================================

    # Sākotnējo datu filtrēšana.
    # Izslēdzam NaN/inf koordinātas un ātruma komponentes.
    x_raw = np.asarray(x, dtype=float).ravel()
    y_raw = np.asarray(y, dtype=float).ravel()
    u_raw = np.asarray(u, dtype=float).ravel()
    v_raw = np.asarray(v, dtype=float).ravel()

    finite = (np.isfinite(x_raw) & np.isfinite(y_raw) &
        np.isfinite(u_raw) & np.isfinite(v_raw))

    positions_all = np.column_stack([x_raw[finite], y_raw[finite]])

    vectors_all = np.column_stack([u_raw[finite], v_raw[finite]])

    if len(positions_all) < 4:
        raise ValueError("Nepietiek derīgu ātruma vektoru interpolācijai.")

    # Noņemam atkārtotas koordinātas, ja tādas ir.
    # Ja vienā punktā ir vairāki vektori, saglabājam pirmo.
    _, unique_idx = np.unique(positions_all, axis=0, return_index=True)
    unique_idx = np.sort(unique_idx)

    positions_all = positions_all[unique_idx]
    vectors_all = vectors_all[unique_idx]

    x_data = positions_all[:, 0]
    y_data = positions_all[:, 1]
    u_data = vectors_all[:, 0]
    v_data = vectors_all[:, 1]
    N_data = len(positions_all)
    print(f"Valid unique velocity vectors: {N_data}")
    
    # ============================================================
    # 3. ATTĒLA KOORDINĀTAS — BEZ TRANSFORMĀCIJAS
    # x pieaug pa labi; y pieaug uz leju.
    # u un v paliek sākotnējās attēla koordinātu komponentes.
    # ============================================================
    
    positions_interp = positions_all.copy()
    vectors_interp = vectors_all.copy()
    
    # Do not flip just v while keeping image-down coordinates and grid.
    X_interp = X
    Y_interp = Y
    
    # ============================================================
    # 1. DIVERGENCE-FREE RBF
    # ============================================================
    
    support_radii = arrow_step * 3
    div_free_interp = dfi.interpolant(nu=5, k=3, dim=2)
    div_free_interp.condition(positions_interp, vectors_interp,
        support_radii, method="SVD")
    
    result_rbf = div_free_interp(X_interp, Y_interp)
    U_rbf = result_rbf[..., 0]
    V_rbf = result_rbf[..., 1]
    speed_rbf = np.hypot(U_rbf, V_rbf)
    
    # ============================================================
    # 2. LINEAR INTERPOLATION COMPARISON
    # ============================================================
    
    U_linear = griddata(positions_interp, vectors_interp[:, 0],
        (X_interp, Y_interp), method="linear") 
    V_linear = griddata(positions_interp, vectors_interp[:, 1],
        (X_interp, Y_interp), method="linear") 
    speed_linear = np.hypot(U_linear, V_linear)
    mask_linear_valid = (np.isfinite(U_linear) & np.isfinite(V_linear))


    # ============================================================
    # 3. DISTANCE TO THE NEAREST MEASUREMENT
    # ============================================================

    tree = cKDTree(positions_all)
    distance_to_data, _ = tree.query(np.column_stack([X.ravel(), Y.ravel()]))
    distance_to_data = distance_to_data.reshape(ny, nx)

    # For visualization
    max_supported_distance = 2.0 * arrow_step
    mask_far_from_data = (distance_to_data > max_supported_distance)

    # ============================================================
    # 4. HOLD-OUT VALIDATION
    # ============================================================
    # Izslēdzam 20% reālo vektoru, interpolējam pēc pārējiem
    # un prognozējam ātrumus izslēgtajās pozīcijās.
    # Tā ir neatkarīgāka pārbaude nekā kļūda apmācības punktos.

    rng = np.random.default_rng(42)
    indices = rng.permutation(N_data)
    
    n_test = max(1, int(0.2 * N_data))
    test_idx = indices[:n_test]
    train_idx = indices[n_test:]
    
    validation_rmse = np.nan
    validation_mae = np.nan
    validation_relative_rmse = np.nan
    
    if len(train_idx) >= 4:
        try:
            validation_interp = dfi.interpolant(nu=5, k=3, dim=2)
            validation_interp.condition(positions_interp[train_idx],
                                        vectors_interp[train_idx], support_radii, method="SVD")
    
            test_result = validation_interp(x_data[test_idx], y_data[test_idx])
            test_result = np.asarray(test_result).reshape(-1, 2)
            test_true = vectors_interp[test_idx]
    
            errors = np.linalg.norm(test_result - test_true, axis = 1)
            finite_errors = errors[np.isfinite(errors)]
    
            if finite_errors.size > 0:
                validation_rmse = np.sqrt(np.mean(finite_errors**2))
                validation_mae = np.mean(finite_errors)
                reference_speed = np.sqrt(np.mean(np.sum(test_true**2, axis=1)))
    
                validation_relative_rmse = (validation_rmse / reference_speed
                    if reference_speed > 0 else np.nan)
    
        except Exception as exc:
            print("Hold-out validation failed:", exc)
    
    print("\n--- RBF hold-out validation ---")
    print(f"Test vectors: {n_test}")
    
    if np.isfinite(validation_rmse):
        print(f"RMSE: {validation_rmse:.4e} m/s")
        print(f"MAE: {validation_mae:.4e} m/s")
        print("Relative RMSE: "f"{validation_relative_rmse:.2%}"
            if np.isfinite(validation_relative_rmse)
            else "Relative RMSE: undefined")
    else:
        print("Validation error could not be calculated.")

    # ============================================================
    # 5. SELECT THE FIELD USED DOWNSTREAM
    # ============================================================
    # Explicitly select a field; RBF holdout diagnostics do not validate
    # a different production interpolant. Keep the image-down vector basis.
    if INTERPOLATION_METHOD == "rbf":
        U, V = U_rbf.copy(), V_rbf.copy()
    elif INTERPOLATION_METHOD == "linear":
        U, V = U_linear.copy(), V_linear.copy()
    else:
        raise RuntimeError("Unexpected interpolation method")
    if U.shape != X.shape or V.shape != X.shape:
        raise ValueError("Velocity grid shape differs from calibrated image grid")
    finite_selected = np.isfinite(U) & np.isfinite(V)
    n_bad = int(np.count_nonzero(~finite_selected))
    if n_bad:
        raise ValueError(
            f"Refusing physical metrics: {INTERPOLATION_METHOD} has {n_bad}/{U.size} "
            "nonfinite grid cells. Establish a validated support/boundary policy first."
        )
    print(f"Selected {INTERPOLATION_METHOD} field: 100% finite grid ({U.size} cells)")
    speed = np.hypot(U, V)
    
    # ============================================================
    # 6. FOUR-PANEL DIAGNOSTIC PLOT
    # ============================================================
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 11))
    # Panel 1: measured velocities.
    ax = axes[0, 0]
    im0 = ax.imshow(C_in_percent, cmap="gray", origin="upper",
        extent=[0, w, h, 0], aspect="equal") 
    sc0 = ax.scatter(x_data, y_data, c=np.hypot(u_data, v_data),
        cmap="turbo", s=14, edgecolors="none")
    ax.quiver(x_data, y_data, u_data, v_data, color="white",
        angles="xy", scale_units="xy", scale=None, width=0.0025)
    fig.colorbar(sc0, ax=ax, label="Measured speed [m/s]")
    ax.set_title("1. Measured OFV vectors")
    
    # Panel 2: RBF speed.
    ax = axes[0, 1]
    im1 = ax.imshow(speed_rbf, origin="upper", extent=[0, w, h, 0],
        cmap="turbo", aspect="equal")
    fig.colorbar(im1, ax=ax, label="RBF speed [m/s]")
    # Vektoru retināšana, lai grafiks nekļūtu pārblīvēts.
    arrow_skip = max(1, int(np.ceil(3 / max(1, arrow_step))))
    ax.quiver(X[::arrow_skip, ::arrow_skip], Y[::arrow_skip, ::arrow_skip],
        U_rbf[::arrow_skip, ::arrow_skip], V_rbf[::arrow_skip, ::arrow_skip],
        color="white", angles="xy", scale_units="xy", scale=None, width=0.002)
    ax.set_title("2. Divergence-free RBF velocity")
    
    # Panel 3: linear interpolation and missing areas.
    ax = axes[1, 0]
    # Bija šis: extent=[0, w, h, 0],mainīt uz extent=[0, w, 0, h]???.
    im2 = ax.imshow(np.ma.masked_invalid(speed_linear), origin="upper",
        extent=[0, w, h, 0], cmap="turbo", aspect="equal")
    fig.colorbar(im2, ax=ax, label="Linear speed [m/s]")
        # Linear interpolation velocity vectors
    ax.quiver(X[::arrow_skip, ::arrow_skip], Y[::arrow_skip, ::arrow_skip],
        U_linear[::arrow_skip, ::arrow_skip], V_linear[::arrow_skip, ::arrow_skip],
        color="white", angles="xy", scale_units="xy", scale=None, width=0.002)
    ax.set_title("3. Linear interpolation;")
    
    # Panel 4: distance to nearest measurement.
    ax = axes[1, 1]
    im3 = ax.imshow(distance_to_data, origin="upper", extent=[0, w, h, 0],
        cmap="magma", aspect="equal") 
    fig.colorbar(im3, ax=ax, label="Distance to nearest vector [px]")
    ax.contour(X, Y, distance_to_data, levels=[max_supported_distance], 
               colors="cyan",linewidths=1.2)
    ax.set_title(f"4. Data distance; cyan = {max_supported_distance:g} px")
    
    for ax in axes.flat:
        ax.set_xlim(0, w)
        ax.set_ylim(h, 0)
        ax.set_xlabel("x [px]")
        ax.set_ylabel("y [px]")
    
    fig.suptitle( f"Velocity interpolation diagnostics | frame {frame_index + 1}",
        fontsize = 14)
    
    fig.tight_layout()
    
    fig.savefig(os.path.join(MASK_CHECK_FOLDER, f"velocity_diagnostics_{frame_index:05d}.png"),
        dpi=180, bbox_inches="tight")
    
    plt.show()
    plt.close(fig)
    
    print("Grid points far from measurements: "
        f"{mask_far_from_data.sum()}/{mask_far_from_data.size}")
    print("Linear interpolation coverage: "
        f"{mask_linear_valid.sum()}/{mask_linear_valid.size}")
    print(f"Mean RBF speed: {np.nanmean(speed_rbf):.4e} m/s")
    print(f"Max RBF speed: {np.nanmax(speed_rbf):.4e} m/s")

    # Change lower resolution for rho, mu, alha gallium to flow grid
    # FIX: use scipy.ndimage.zoom instead of stride slicing
    rho_small = zoom(rho, (ny / rho.shape[0], nx / rho.shape[1]))
    mu_small  = zoom(mu,  (ny / mu.shape[0],  nx / mu.shape[1]))
    w_gallium_small = zoom(w_gallium, (ny / w_gallium.shape[0],
                                     nx / w_gallium.shape[1]))
    # speed
    speed = np.sqrt(U**2 + V**2)

    # ========================================================
    # Spatial step
    dx = np.mean(np.diff(x_full_1d)) * delta_x
    dy = np.mean(np.diff(y_full_1d)) * delta_x
    
    # Integral elements
    N = ny * nx   # grid point count
    dV = dx * dy * d   # [m^3] volumes for integrations
    
    # ========================================================
    # Derivatives of the velocity
    du_dy, du_dx = np.gradient(U, dy, dx)
    dv_dy, dv_dx = np.gradient(V, dy, dx)
    grad_u_squared = (du_dx**2 + du_dy**2 + dv_dx**2 + dv_dy**2)
    divergence = du_dx + dv_dy
    
    max_div = np.max(np.abs(divergence))
    mean_div = np.mean(np.abs(divergence))
    # Relatīvais lielums — salīdzina ar tipisko gradienta amplitūdu,
    # lai zinātu, vai diverģence ir "maza" salīdzinājumā ar pašu plūsmu
    full_gradient_norm = np.mean(np.sqrt(du_dx**2 + du_dy**2 + dv_dx**2 + dv_dy**2))
    relative_div = mean_div / (full_gradient_norm + 1e-12)
    print(f"Frame {frame_index + 1}: max|div|={max_div:.3e}, mean|div|={mean_div:.3e}, relative={relative_div:.3%}")
    
    # ========================================================
    # Vorticity
    # Physical +z curl on image y-down axes.
    omega = physical_vorticity_from_image_derivatives(du_dy, dv_dx)
    omega_squared = omega**2 
    # Lokālā viskozā disipācija [W/m^3]
    dissipation = 2 * mu_small * (du_dx**2 + dv_dy**2 + 0.5 * (du_dy + dv_dx)**2)
    # Kinetic energy
    kinetic_energy = 0.5 * rho_small * speed**2
    
    # for checking \epsilon(t) equation....
    # Kopējā kinētiskā enerģija
    K_total = np.sum(kinetic_energy) * dV
    # Kopējā viskozā disipācija [W]
    D_total = np.sum(dissipation) * dV
    # Save time series for kinetic-energy balance analysis
    kinetic_energy_total.append(K_total)
    dissipation_total.append(D_total)
    time_values.append(frame_index * delta_t)

    # =============================================================
    # For checking equation
    # total enstrophy
    # mu_weighted_enstrophy_total = np.sum(mu_small * omega**2) * dV
    # enstrophy_gradu_total = np.sum(grad_u_squared) * dV
    # enstrophy_omega_total = np.sum(omega_squared) * dV
    
    # ============================================================
    # VELOCITY GRADIENT AND VORTICITY INTEGRAL IDENTITY
    # ============================================================
    # In general 
    # For divergence-free flow with suitable boundary conditions:
    # integral(|grad(u)|^2 dV) = integral(omega^2 dV)
    #
    # A discrepancy can arise from:
    # - nonzero divergence,
    # - boundary terms,
    # - numerical differentiation and interpolation errors.
    
    gradient_integral = np.sum(grad_u_squared) * dV
    vorticity_integral = np.sum(omega_squared) * dV
    
    integral_difference = gradient_integral - vorticity_integral
    
    integral_relative_difference = (abs(integral_difference) / (
            abs(gradient_integral) + abs(vorticity_integral) + 1e-12))
    # ========================================================
    # Save nupy arrays


    if atbilde == "yes":
        np.save(os.path.join(NPY_FOLDER, f"vorticity_{frame_index:05d}.npy"), omega)
        np.save(os.path.join(NPY_FOLDER, f"dissipation_{frame_index:05d}.npy"), dissipation)
        np.save(os.path.join(NPY_FOLDER, f"kinetic_energy_{frame_index:05d}.npy"), kinetic_energy)
        np.save(os.path.join(NPY_FOLDER, f"viscosity_{frame_index:05d}.npy"), mu_small)
        np.save(os.path.join(NPY_FOLDER, f"density_{frame_index:05d}.npy"), rho_small)
        np.save(os.path.join(NPY_FOLDER, f"speed_{frame_index:05d}.npy"), speed)
        np.save(os.path.join(NPY_FOLDER, f"enstrophy_field_{frame_index:05d}.npy"), grad_u_squared)
        np.save(os.path.join(NPY_FOLDER, f"gallium_fraction_{frame_index:05d}.npy"), w_gallium_small)
    
    # ========================================================
    # SAVE SUMMARY
    # ========================================================

    summary.append({
        "frame": frame_index,
        "mean_speed": np.mean(speed),
        "max_speed": np.max(speed),
        "mean_vorticity": np.mean(np.abs(omega)),
        "mean_dissipation": np.mean(dissipation),
        "mean_kinetic_energy": np.mean(kinetic_energy),
        "mean_viscosity": np.mean(mu_small),
        "mean_omega_squared": np.mean(omega**2),
        "N": N,
        "dV": dV,
        "Kinetic_energy_total": K_total,
        # "mu_weighted_enstrophy_total": mu_weighted_enstrophy_total,
        "gradient_integral": gradient_integral,
        "vorticity_integral": vorticity_integral,
        "integral_diference": integral_difference,
        "integral_relative_diff": integral_relative_difference
    })


# %% ============================================================
# KINETIC ENERGY BALANCE
# dK/dt + D = epsilon(t)
# ============================================================

kinetic_energy_total = np.asarray(kinetic_energy_total, dtype=float)
dissipation_total = np.asarray(dissipation_total, dtype=float)
time_values = np.asarray(time_values, dtype=float)

if len(time_values) < 3:
    raise ValueError("Nepieciešami vismaz 3 laika kadri, "
        "lai jēgpilnāk novērtētu laika atvasinājumu.")

# ------------------------------------------------------------
# 1. Laika atvasinājums: dK/dt
# ------------------------------------------------------------
# np.gradient izmanto centrālo galīgo diferenču shēmu
# iekšējiem punktiem un vienpusējas starpības pie robežām.

dK_dt = np.gradient(kinetic_energy_total, time_values, edge_order=2)

# ------------------------------------------------------------
# 2. Bilances atlikums epsilon(t)
# ------------------------------------------------------------
# dK/dt + D = epsilon(t)
#
# Ja ideālā bilance dK/dt + D = 0 ir spēkā,
# epsilon(t) vajadzētu būt tuvu nullei.

epsilon_t = dK_dt + dissipation_total

# ------------------------------------------------------------
# 3. Relatīvais atlikums
# ------------------------------------------------------------
# Normalizējam pēc tipiskā enerģijas izmaiņas un
# disipācijas lieluma, lai rezultātus būtu vieglāk salīdzināt.

scale = np.abs(dK_dt) + np.abs(dissipation_total)

epsilon_relative = np.divide(np.abs(epsilon_t), scale, 
                             out=np.full_like(epsilon_t, np.nan), where=scale > 1e-14)

# ------------------------------------------------------------
# 4. Saglabājam rezultātus CSV
# ------------------------------------------------------------
balance_df = pd.DataFrame({
    "time_s": time_values,
    "kinetic_energy_J": kinetic_energy_total,
    "dK_dt_W": dK_dt,
    "dissipation_W": dissipation_total,
    "epsilon_t_W": epsilon_t,
    "relative_residual": epsilon_relative
})

balance_csv = os.path.join(OUTPUT_FOLDER, "kinetic_energy_balance.csv")
balance_df.to_csv(balance_csv, index=False)

print("\n--- KINETIC ENERGY BALANCE ---")
print(f"Mean |epsilon|: {np.mean(np.abs(epsilon_t)):.6e} W")
print(f"Max  |epsilon|: {np.max(np.abs(epsilon_t)):.6e} W")
print(f"Mean relative residual: "
      f"{np.nanmean(epsilon_relative):.3%}")

# ------------------------------------------------------------
# 5. Grafiki
# ------------------------------------------------------------

fig, axes = plt.subplots(3, 1, figsize=(9, 12))

axes[0].plot(time_values, kinetic_energy_total, "o-")
axes[0].set_ylabel("Kinetic energy [J]")
axes[0].set_title("Total kinetic energy")
axes[0].grid(True)

axes[1].plot(time_values, dK_dt, "o-", label=r"$dK/dt$")
axes[1].plot(time_values, -dissipation_total, "s--", label=r"$-\mathcal{D}$")
axes[1].set_ylabel("Power [W]")
axes[1].set_title("Energy balance terms")
axes[1].legend()
axes[1].grid(True)

axes[2].plot(time_values, epsilon_t, "o-")
axes[2].axhline(0, linestyle="--", color="black")
axes[2].set_xlabel("Time [s]")
axes[2].set_ylabel(r"$\epsilon(t)$ [W]")
axes[2].set_title("Kinetic-energy balance residual")
axes[2].grid(True)

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_FOLDER, "kinetic_energy_balance.png"), 
    dpi=180)
plt.show()

plt.figure(figsize=(8, 4))
plt.plot(time_values, 100 * epsilon_relative, "o-")
plt.xlabel("Time [s]")
plt.ylabel("Relative residual [%]")
plt.title("Relative kinetic-energy balance residual")
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_FOLDER, "kinetic_energy_balance_relative.png"),
    dpi=180)
plt.show()

print(f"Results saved to: {balance_csv}")

# %% ============================================================
# Calculate common color ranges for all frames
# ============================================================

if atbilde == "yes":

    print("\nCalculating common color ranges for all fields...")

    # ------------------------------------------------------------
    # Fields where the range will be calculated from all frames
    # ------------------------------------------------------------

    dynamic_fields = [
        "speed",
        # "vorticity",
        "enstrophy_field",
        "dissipation",
        "kinetic_energy",
        "density",
        "viscosity",
        "gallium_fraction"
    ]

    # Here we will store:
    # field_ranges["speed"] = [vmin, vmax]
    # field_ranges["vorticity"] = [vmin, vmax]
    # etc.

    field_ranges = {}
    # ------------------------------------------------------------
    # Calculate range for dynamic fields
    # ------------------------------------------------------------

    for name in dynamic_fields:
        print(f"Finding range for: {name}")
        all_values = []
        field_files = sorted(glob.glob(os.path.join(NPY_FOLDER, f"{name}_*.npy")))

        # Read every frame
        for file_path in field_files:
            field = np.load(file_path)
            # Remove NaN and infinity
            valid_values = field[np.isfinite(field)]
            if valid_values.size > 0:
                all_values.append(valid_values)

        # Combine values from all frames
        if len(all_values) > 0:
            all_values = np.concatenate(all_values)
            # Instead of absolute min/max, use 1st and 99th percentile.
            # This prevents one extreme outlier from destroying the color scale.
            vmin = np.percentile(all_values, 1)
            vmax = np.percentile(all_values, 99)
            

            # These fields cannot physically be negative
            if name in ["speed", "enstrophy_field", "dissipation", "kinetic_energy",
                    "density", "viscosity", "gallium_fraction"]:
                vmin = max(0, vmin)

            field_ranges[name] = [float(vmin), float(vmax)]
            print(f"  {name}: " f"vmin = {vmin:.6e}, " f"vmax = {vmax:.6e}")

    # ------------------------------------------------------------
    # Vorticity
    # ------------------------------------------------------------
    # Vorticity can be positive or negative.
    # Therefore we make the range symmetric around zero.
    # ------------------------------------------------------------

    print("Finding range for: vorticity")

    all_values = []

    vorticity_files = sorted(
        glob.glob(os.path.join(NPY_FOLDER, "vorticity_*.npy")))

    for file_path in vorticity_files:
        omega = np.load(file_path)
        valid_values = omega[np.isfinite(omega)]

        if valid_values.size > 0:
            all_values.append(valid_values)

    if len(all_values) > 0:
        all_values = np.concatenate(all_values)
        omega_min = np.percentile(all_values, 1)
        omega_max = np.percentile(all_values, 99)

        # Make symmetric around zero
        omega_limit = max(abs(omega_min), abs(omega_max))
        field_ranges["vorticity"] = [float(-omega_limit), float(omega_limit)]
        print(f" vorticity: " f"vmin = {-omega_limit:.6e}, " f"vmax = {omega_limit:.6e}")

    print("\nFinal common ranges:")

    for name, limits in field_ranges.items():
        print(f"{name:20s}: " f"{limits[0]:.6e} -> " f"{limits[1]:.6e}")
        

# %% ============================================================
# Plot all fields using common ranges
# ============================================================

if atbilde == "yes":
    print("\nCreating plots with common color ranges...")

    for name, limits in field_ranges.items():
        print(f"Plotting: {name}")
        field_files = sorted(glob.glob(os.path.join(NPY_FOLDER, f"{name}_*.npy")))

        for file_path in field_files:
            field = np.load(file_path)
            # ----------------------------------------------------
            # Get frame number from filename
            #
            # Example:
            # density_00025.npy
            #
            # -> frame_number = 25
            # ----------------------------------------------------

            filename = os.path.basename(file_path)
            frame_number = int(filename.split("_")[-1].split(".")[0])
            # ----------------------------------------------------
            # Create plot
            # ----------------------------------------------------
        
            plt.figure(figsize=(6, 5))
            # Convert viscosity from Pa*s to mPa*s for plotting only
            if name == "viscosity":
                plot_field = field * 1000
                plot_limits = [v * 1000 for v in limits]
                colorbar_label = "Dynamic viscosity [mPa·s]"
            else:
                plot_field = field
                plot_limits = limits
                colorbar_label = name
            
            plt.imshow(plot_field, origin="upper", aspect="auto",
                vmin=plot_limits[0], vmax=plot_limits[1])
            plt.colorbar(label=colorbar_label)
            plt.title(f"{name} | frame {frame_number + 1}")
            
            plt.tight_layout()

            # ----------------------------------------------------
            # Save
            # ----------------------------------------------------
            plt.savefig(os.path.join(PLOTS_FOLDER, name,
                    f"{name}_{frame_number:05d}.png"), dpi=150)
            plt.close()
    print("All plots created.")
    
# %% Save CSV summary

summary_df = pd.DataFrame(summary)
 
if atbilde == "yes":
    summary_csv = os.path.join(OUTPUT_FOLDER, "summary.csv")
    summary_df.to_csv(summary_csv, index=False)
    print("\nDONE.")
    print(f"Summary saved to: {summary_csv}")
else:
    print("\nDONE.")
    print("Files have not been saved (user selected 'n').")

# Check equation
# ============================================================
# Kinētiskās enerģijas disipācijas pārbaude

t = summary_df["frame"].to_numpy() * delta_t
I_gradu = summary_df["gradient_integral"].to_numpy()
I_omega = summary_df["vorticity_integral"].to_numpy()
rel_diff  = summary_df["integral_relative_diff"].to_numpy()

# --- Absolūtās vērtības laikā ---
plt.figure(figsize=(8,5))
plt.plot(t, I_gradu, label=r"$\int \|\nabla u\|^2\,dV$")
plt.plot(t, I_omega, "--", label=r"$\int \|\omega\|^2\,dV$")
plt.xlabel("Laiks [s]")
plt.ylabel(r"Enstrofija [s$^{-2}$·m$^3$]")   # pārbaudi vienības atbilstoši dV
plt.legend()
plt.title(r"$\|\nabla u\|^2$ vs $\|\omega\|^2$ integrāļu salīdzinājums")
plt.tight_layout()
if atbilde == "yes":
    plt.savefig(os.path.join(OUTPUT_FOLDER, "enstrophy_identity_check.png"))
plt.show()

# --- Relatīvā starpība laikā ---
plt.figure(figsize=(8,4))
plt.plot(t, rel_diff * 100)
plt.axhline(np.mean(rel_diff) * 100, color='r', linestyle='--',
            label=f"Vidējā = {np.mean(rel_diff):.1%}")
plt.xlabel("Laiks [s]")
plt.ylabel("Relatīvā starpība [%]")
plt.legend()
plt.title(r"Relatīvā starpība: $\|\nabla u\|^2$ vs $\|\omega\|^2$")
plt.tight_layout()
if atbilde == "yes":
    plt.savefig(os.path.join(OUTPUT_FOLDER, "enstrophy_identity_relative_error.png"))
plt.show()

print(f"Vidējā relatīvā starpība: {np.mean(rel_diff):.2%}")
print(f"Maksimālā relatīvā starpība: {np.max(rel_diff):.2%}")
print(f"Mediānas relatīvā starpība: {np.median(rel_diff):.2%}")
