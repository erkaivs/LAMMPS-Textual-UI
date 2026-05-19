import os
import numpy as np
import matplotlib.pyplot as plt


def main(al_file: str, cu_file: str, result_dir: str):

    os.makedirs(result_dir, exist_ok=True)

    if not os.path.exists(al_file):
        raise FileNotFoundError(f"Al file not found: {al_file}")

    if not os.path.exists(cu_file):
        raise FileNotFoundError(f"Cu file not found: {cu_file}")

    # ==== LOAD DATA ====
    Al_diff = np.loadtxt(al_file, skiprows=2)
    Cu_diff = np.loadtxt(cu_file, skiprows=2)

    # ==== TIME (ps → s) ====
    time_ps = Al_diff[:, 0]
    time_s = (time_ps - time_ps[0]) * 1e-12

    # ==== MSD ====
    msdAl_A2 = Al_diff[:, 1]
    msdCu_A2 = Cu_diff[:, 1]

    # ==== LINEAR REGION ====
    start_index = int(0.2 * len(time_ps))

    time_ps_lin = time_ps[start_index:]
    msdAl_lin = msdAl_A2[start_index:]
    msdCu_lin = msdCu_A2[start_index:]

    # ==== FIT ====
    slope_Al_A2ps, intercept_Al = np.polyfit(
        (time_ps_lin - time_ps_lin[0]),
        msdAl_lin,
        1
    )

    slope_Cu_A2ps, intercept_Cu = np.polyfit(
        (time_ps_lin - time_ps_lin[0]),
        msdCu_lin,
        1
    )

    # ==== CONVERT ====
    slope_Al_m2s = slope_Al_A2ps * 1e-8
    slope_Cu_m2s = slope_Cu_A2ps * 1e-8

    D_Al = slope_Al_m2s / 6
    D_Cu = slope_Cu_m2s / 6

    jobname = os.path.splitext(os.path.basename(al_file))[0].split("_")[0]

    # ==== PLOT ====
    plt.figure(figsize=(7, 5), dpi=300)

    plt.scatter(time_ps, msdAl_A2, s=8, alpha=0.6, label="Al MSD")
    plt.plot(
        time_ps_lin,
        slope_Al_A2ps * (time_ps_lin - time_ps_lin[0]) + intercept_Al,
        linewidth=2,
        label="Al linear fit"
    )

    plt.scatter(time_ps, msdCu_A2, s=8, alpha=0.6, label="Cu MSD")
    plt.plot(
        time_ps_lin,
        slope_Cu_A2ps * (time_ps_lin - time_ps_lin[0]) + intercept_Cu,
        linewidth=2,
        label="Cu linear fit"
    )

    plt.xlabel("Time (ps)")
    plt.ylabel("MSD (Å²)")
    plt.title(f"{jobname}: MSD and Linear Fit")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()

    plt.savefig(os.path.join(result_dir, f"{jobname}_diffusion.png"))
    plt.close()

    # ==== SAVE NUMERIC RESULT ====
    with open(os.path.join(result_dir, f"{jobname}_diffusion_coeff.txt"), "w") as f:
        f.write("=== HEATHOLD DIFFUSION RESULT ===\n")
        f.write(f"Slope_Al (Å²/ps) = {slope_Al_A2ps:.6e}\n")
        f.write(f"Slope_Cu (Å²/ps) = {slope_Cu_A2ps:.6e}\n\n")
        f.write(f"D_Al (m²/s) = {D_Al:.6e}\n")
        f.write(f"D_Cu (m²/s) = {D_Cu:.6e}\n")

    return True

if __name__ == "__main__":
    BASE_DIR = os.path.expanduser("~/lmpui")

    al_file = os.path.join(BASE_DIR, "output", "heathold", "01msd_Al.txt")
    cu_file = os.path.join(BASE_DIR, "output", "heathold", "01msd_Cu.txt")
    result_dir = os.path.join(BASE_DIR, "result", "heathold")

    main(al_file, cu_file, result_dir)
