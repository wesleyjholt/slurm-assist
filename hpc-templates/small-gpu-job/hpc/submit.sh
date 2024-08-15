#!/bin/bash

if [ -z "$1" ]; then
  echo "Error: No run name provided."
  echo "Usage: $0 <RUN_NAME>"
  exit 1
fi

# Set up environment
export RUN_NAME=$1
source _do_all_config.sh

# Clean up from previous runs
rm -rf $RESULTS_DIR
rm -rf $TMP_DIR

# Run main computations
sbatch -A $ACCOUNT --nodes $NODES --ntasks $NTASKS --gpus-per-node $GPUS_PER_NODE --mem-per-cpu $MEM_PER_CPU --time $WALLTIME _run.sh
