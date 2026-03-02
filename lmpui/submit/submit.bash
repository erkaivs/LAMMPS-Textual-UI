#!/bin/bash
#SBATCH --job-name=JOBNAME
#SBATCH --output=output/JOBNAME.out
#SBATCH --error=output/JOBNAME.err
#SBATCH --ntasks=2
#SBATCH --nodes=1
#SBATCH --partition=guriang

export OMP_PROC_BIND=true
export NUMBA_NUM_THREADS=$SLURM_NPROCS
export OMP_NUM_THREADS=$SLURM_NPROCS
export OMPI_MCA_btl_vader_single_copy_mechanism=none

echo "$PWD"
mpirun LMP_PROG -in INPUT_FILE
