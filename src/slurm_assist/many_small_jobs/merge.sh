#!/bin/bash

#SBATCH --job-name=merge
#SBATCH --ntasks=1
#SBATCH --time=0:15:00

module purge

# Set up tracking
module load utilities monitor
monitor cpu percent >cpu-percent-merge.log &
CPU_PID=$!

# Run computations
apptainer run $CONTAINER_IMAGE merge_results.py $@

# Shut down the resource monitors
kill -s INT $CPU_PID