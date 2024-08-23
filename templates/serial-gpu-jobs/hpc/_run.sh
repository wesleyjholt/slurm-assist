#!/bin/bash

# Set up environment
source _do_all_config.sh
module purge

# Check CUDA version
nvcc --version

# Set up tracking
module load utilities monitor

# Track GPU load
monitor gpu percent >gpu-percent.log &
GPU_PID=$!

# Track CPU load
monitor cpu percent >cpu-percent.log &
CPU_PID=$!

# Make directories
mkdir -p $RESULTS_DIR
mkdir -p $TMP_DIR

# Run the command(s) to execute the job
apptainer run --nv $CONTAINER_IMAGE "$RUN_NAME/run.py" --results $RESULTS_DIR --tmp $TMP_DIR

# Clean up
rm -rf $TMP_DIR

# Shut down the resource monitors
kill -s INT $GPU_PID $CPU_PID