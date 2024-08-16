#!/bin/bash

set_env_vars=`python3 parse_args.py $@`
eval "$set_env_vars"
source _do_all_config.sh

# Clean up from previous runs
rm -rf $RESULTS_DIR
rm -rf $TMP_DIR

# Run main computations
sbatch -A $ACCOUNT --nodes $NODES --ntasks $NTASKS --gpus-per-node $GPUS_PER_NODE --mem-per-cpu $MEM_PER_CPU --time $WALLTIME _run.sh
