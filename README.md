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

DockerHub Images already been published, users only need:

```bash
git clone https://github.com/erkaivs/LAMMPS-Textual-UI.git
cd LAMMPS-Textual-UI
docker compose pull
docker compose up -d head
docker compose up -d node
```
Kindly add node01-04 each one line command to avoid clash and instant node shutdown. 

To activate the container:

```bash
docker exec -ti lmphead bash
```

This will automatically put the user into an environment named venv. There will be two folders, and click the lmpui folder name.

Inside the lmpui folder exist lmpui_template and the program named LMP_NR.py. If the users want to run a program, start with typing this in the terminal:

```bash
chmod +x LMP_NR.py
./LMP_NR.py
```
This should open the program of LAMMPS Textual User Interface.

---

## How does the program works?

This prototype made solely for the Liebniz Fast Calculation MDS Competition, whereas required a diffusion study between Copper (Cu) and Aluminum (Al) using the Embedded Atom Method potential, calculating the diffusion coefficient of Aluminum initially placed on top of a Copper using Lammps.

Running one long simulation costs a lot of time, and still not guaranteed to run smoothly. Therefore, making the simulation structured with separated each stage restart files can prevent inaccuracy while minimizing wasted time, and running multiple simulations simultaneously . The limited computational hardware and comprehension aspire this program runs easily with just a click of button in the Textual UI. As someone who just got introduced with MSD and LAMMPS, this UI can make the learning process easier and more organized simulations runs for Al-Cu diffusion. 

As the program ran, the UI would show options for simulation. Each simulation has the same diffusion stage, and each stage has run (the infiles), queue that shows the submitted job, analysis with plot graphic result that directly goes to result folder, cancel the queue, and the button back. Users also can open (read and edit) files, new files, and delete files. Every output placed in one folder, users can check manually in the output folder inside each used sim. 

---

## DISCLAIMER

This program is still developing. Many features will be added!
