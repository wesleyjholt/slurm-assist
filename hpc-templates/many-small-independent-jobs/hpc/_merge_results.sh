#!/bin/bash

#SBATCH --job-name=merge_results

# Set up environment
source _do_all_config.sh
module purge

# Set up tracking
module load utilities monitor
monitor cpu percent >cpu-percent-merge.log &
CPU_PID=$!

# Run computations
apptainer run $CONTAINER_IMAGE merge_results.py -nj $ARRAY_SIZE -np $NTASKS_PER_JOB --results $RESULTS_DIR --tmp $TMP_DIR

# Clean up
rm -rf $TMP_DIR

# Shut down the resource monitors
kill -s INT $CPU_PID