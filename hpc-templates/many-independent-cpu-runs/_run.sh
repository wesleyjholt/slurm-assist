#!/bin/bash

#SBATCH --job-name=job
#SBATCH --time=0:10:00
#SBATCH --mem-per-cpu=512M

# ===================== #
# USER INPUTS
BATCHED_DATA_DIR=$1
BATCHED_RESULTS_DIR=$2
OUTPUT_FILE=$3
ENVIRONMENT=$4
# ===================== #

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
mpirun -n $SLURM_NTASKS python3 run.py --job-id $(($SLURM_ARRAY_TASK_ID - 1)) -i $BATCHED_DATA_DIR -o $BATCHED_RESULTS_DIR

# shut down the resource monitors
kill -s INT $CPU_PID