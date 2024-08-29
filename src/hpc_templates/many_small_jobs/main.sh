#!/bin/bash

#SBATCH --job-name=main

module purge

# Set up tracking
module load utilities monitor
monitor cpu percent >cpu-percent-run.log &
CPU_PID=$!

# Run computations
srun --mpi=pmi2 apptainer run $CONTAINER_IMAGE run.py --job-id $SLURM_ARRAY_TASK_ID $@

# Shut down the resource monitors
kill -s INT $CPU_PID