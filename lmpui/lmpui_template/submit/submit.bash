#!/bin/bash
#SBATCH --job-name=JOBNAME
#SBATCH --output=JOBNAME.out
#SBATCH --error=JOBNAME.err
#SBATCH --ntasks=2
#SBATCH --nodes=1
#SBATCH --partition=guriang

export OMP_PROC_BIND=true
export NUMBA_NUM_THREADS=$SLURM_NPROCS
export OMP_NUM_THREADS=$SLURM_NPROCS
export OMPI_MCA_btl_vader_single_copy_mechanism=none

cd "$SLURM_SUBMIT_DIR"

echo "$PWD"
mpirun /home/share/bin/lmp_mpi -in INPUT_FILE
