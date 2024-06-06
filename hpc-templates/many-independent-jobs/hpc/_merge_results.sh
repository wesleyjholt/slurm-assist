#!/bin/bash

#SBATCH --job-name=merge_results

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
python3 -m ${HPC_DIR}.merge_results -nj $ARRAY_SIZE -np $NTASKS_PER_JOB -i $BATCHED_RESULTS_DIR -o $OUTPUT_FILE

# shut down the resource monitors
kill -s INT $CPU_PID