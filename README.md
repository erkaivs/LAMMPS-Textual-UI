# LAMMPS Textual User Interface

## What is LAMMPS?
LAMMPS (Large-scale Atomic/Molecular Massively Parallel Simulator) is an open-source molecular dynamics simulation software designed for particle-based modeling of materials at the atomic scale.

Official website:  
https://www.lammps.org/

LAMMPS supports:
- Classical molecular dynamics
- Parallel computation (MPI)
- Multiple interatomic potentials (EAM, Lennard-Jones, etc.)
- Customizable ensembles and boundary conditions

---

## Why a Textual UI?

LAMMPS operates through command-line input scripts. While flexible, this approach can:

- Increase configuration errors
- Fragment simulation stages
- Reduce workflow traceability
- Complicate reproducibility across machines

This project introduces a structured Textual User Interface (Textual UI) that:

- Enforces deterministic simulation stages
- Automates restart handling
- Integrates post-processing (e.g., MSD analysis)
- Reduces manual shell interaction

The UI preserves full transparency of LAMMPS scripting while adding workflow control.

---

## Containerized Execution with Docker

To ensure reproducibility and portability, the entire execution environment is containerized using Docker.

The Docker image includes:

- LAMMPS compiled with MPI and MANYBODY package
- Slurm workload manager
- SSH and Munge services
- Pre-configured environment variables
- Embedded Textual UI application

This eliminates dependency inconsistencies across systems.

---

## Running the System

Prebuilt images are available on DockerHub, users only need:

```bash
git clone https://github.com/erkaivs/LAMMPS-Textual-UI.git
cd LAMMPS-Textual-UI
docker compose pull
docker compose up -d head
docker compose up -d node
```
Kindly add node01-04 each one line command to avoid clash and instant node shutdown. 

To activate and access the head container:

```bash
docker exec -ti lmphead bash
cd lmpui
```

This will automatically put the user into an environment named venv. 
There will be two folders, and click the lmpui folder name.

Inside the lmpui folder, exists lmpui_template and the program named LMP_NR.py. 
If the users want to run the program, type this to the terminal:

```bash
chmod +x LMP_NR.py
./LMP_NR.py
```
This should start the LAMMPS Textual User Interface.

---

## How does the program works?

This prototype was developed for the Leibniz Fast Calculation MDS Competition, focusing on a diffusion study between Aluminum (Al) and Copper (Cu) using the Embedded Atom Method (EAM) potential. The primary objective is to compute the diffusion coefficient of Aluminum atoms initially placed on a Copper substrate through Mean Square Displacement (MSD) analysis within LAMMPS.

Running a single continuous simulation for this purpose is computationally expensive and prone to instability or failure, which can lead to significant time loss. To address this, the system restructures the simulation into deterministic, stage-based segments using restart files. This approach improves reliability, reduces wasted computation, and enables multiple simulations to run in parallel under limited hardware constraints.

The TUI organizes simulation into structured stages.

Each simulation provides:

- Run: execute LAMMPS input scripts
- Queue: monitor submitted jobs (Slurm)
- Analysis: automatic MSD plotting and result export
- Cancel: terminate queued/running jobs
- File Management: create, edit, delete input files

Every output placed in one folder, and analysis results into the result folder. Users has to check manually in the output folder of the current working simulation folder due to limited access to the terminal. 

Reminder that the dump files can only be played with external software Ovito and the plot analysis results must be saved to local computer to view the images. 
Ovito is a software to visualize and explore particle simulations of any kind and size. Users can load file in Ovito with logs format such as .lammpstrj or for example dump_relax.* (the symbol (*) indicates numbers of steps). 

Official Ovito website:  
https://www.ovito.org/

---

## DISCLAIMER

This program is still improving. Many features will be added!
