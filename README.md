# lmpcluster  
Containerized LAMMPS + Slurm Cluster with Textual UI Orchestration
A reproducible molecular dynamics execution framework built on Docker, Slurm, and a Python-based Textual User Interface.

## From repository root:

git clone [<repo>](https://github.com/erkaivs/LAMMPS-Textual-UI/)
docker compose pull
docker compose up -d

Check the running container:
docker ps

To access the head node:
docker exec -it lmphead bash

Check the slurm status:
sinfo
squeue 
