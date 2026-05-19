import os
import pandas as pd
import matplotlib.pyplot as plt


def read_lammps_thermo(fname):
    data = []
    columns = None

    with open(fname, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if line.startswith("Step"):
                columns = line.split()
                continue

            if columns is not None:
                parts = line.split()
                if len(parts) == len(columns):
                    try:
                        data.append([float(x) for x in parts])
                    except:
                        pass

    return pd.DataFrame(data, columns=columns)


def main(log_path: str, result_dir: str):
    os.makedirs(result_dir, exist_ok=True)

    if not os.path.exists(log_path):
        raise FileNotFoundError(f"Log file not found: {log_path}")

    df = read_lammps_thermo(log_path)

    jobname = os.path.splitext(os.path.basename(log_path))[0]

    # === TEMPERATURE ===
    plt.figure()
    plt.plot(df["Step"], df["Temp"])
    plt.xlabel("Step")
    plt.ylabel("Temperature (K)")
    plt.title(f"{jobname}: Temperature vs Step")
    plt.grid()
    plt.savefig(os.path.join(result_dir, f"{jobname}_temperature.png"))
    plt.close()

    # === POTENTIAL ENERGY ===
    plt.figure()
    plt.plot(df["Step"], df["PotEng"])
    plt.xlabel("Step")
    plt.ylabel("Potential Energy")
    plt.title(f"{jobname}: Potential Energy vs Step")
    plt.grid()
    plt.savefig(os.path.join(result_dir, f"{jobname}_poteng.png"))
    plt.close()

    # === PRESSURE ===
    plt.figure()
    plt.plot(df["Step"], df["Press"])
    plt.xlabel("Step")
    plt.ylabel("Pressure")
    plt.title(f"{jobname}: Pressure vs Step")
    plt.grid()
    plt.savefig(os.path.join(result_dir, f"{jobname}_pressure.png"))
    plt.close()

    return True

if __name__ == "__main__":
    main()
