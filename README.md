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

Once the images are published to Docker Hub, users only need:

```bash
git clone https://github.com/erkaivs/LAMMPS-Textual-UI.git
cd LAMMPS-Textual-UI
docker compose pull
docker compose up -d
```

To activate the container:
```bash
docker exec -ti lmphead bash
```
