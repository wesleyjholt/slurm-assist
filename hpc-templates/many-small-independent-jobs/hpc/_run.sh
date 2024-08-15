#!/bin/bash

#SBATCH --job-name=run

# Set up environment
source _do_all_config.sh
module purge

# Set up tracking
module load utilities monitor
monitor cpu percent >cpu-percent-run.log &
CPU_PID=$!

# Run computations
srun --mpi=pmi2 apptainer run $CONTAINER_IMAGE run.py --job-id $(($SLURM_ARRAY_TASK_ID - 1)) --results $RESULTS_DIR --tmp $TMP_DIR

# Shut down the resource monitors
kill -s INT $CPU_PID