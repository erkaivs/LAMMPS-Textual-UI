import numpy as np
import os

BASE_DIR = os.path.expanduser("~/lmpui")
MSD_DIR = os.path.join(BASE_DIR, "output", "msd")

RUNS = 10
T_MIN = 100000
T_MAX = 300000

def compute_diffusion(msd_path):
    data = np.loadtxt(msd_path, skiprows=2)

    timestep = data[:, 0]
    msd = data[:, 1]

    time = timestep * 1e-12
    msd = msd * 1e-20

    mask = (timestep >= T_MIN) & (timestep <= T_MAX)

    slope, intercept = np.polyfit(time[mask], msd[mask], 1)

    D = slope / 6.0

    return slope, D


for i in range(1, RUNS + 1):

    file_Al = os.path.join(MSD_DIR, f"{i:02d}_msd_Al.txt")
    file_Cu = os.path.join(MSD_DIR, f"{i:02d}_msd_Cu.txt")

    slope_Al, D_Al = compute_diffusion(file_Al)
    slope_Cu, D_Cu = compute_diffusion(file_Cu)

    print(f"Run {i:02d}")
    print("Slope_Al:", slope_Al)
    print("D_Al:", D_Al)
    print("Slope_Cu:", slope_Cu)
    print("D_Cu:", D_Cu)
    print()
