#!/bin/bash

#SBATCH --job-name=run

if [ -z "$RUN_NAME" ]; then
  echo "Error: No variable named RUN_NAME."
  exit 1
fi

source ${HPC_DIR}/config.sh
source ${HPC_DIR}/${RUN_NAME}/config.sh

# Set up tracking
module load utilities monitor

# Track CPU load
monitor cpu percent >cpu-percent.log &
CPU_PID=$!

# Load environment
module load use.own
module load conda-env/$ENVIRONMENT

# Navigate to correct directory
cd $SLURM_SUBMIT_DIR
echo Running job from directory: `pwd`

# Run computations
mpirun -n $SLURM_NTASKS python3 -m ${HPC_DIR}.run --job-id $(($SLURM_ARRAY_TASK_ID - 1)) -i $BATCHED_DATA_DIR -o $BATCHED_RESULTS_DIR

# shut down the resource monitors
kill -s INT $CPU_PID