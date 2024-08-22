#!/bin/bash

# FILE: submit.sh
# PURPOSE: Submit many independent CPU runs to the HPC to run in parallel.
# DESCRIPTION: 
#     Suppose you have 1,000,000 independent cases to run. With this script, you can
#     e.g., 
#          - submit 100 different jobs (ARRAY_SIZE),
#          - each using 100 different CPUs (NTASKS_PER_JOB)
#          - so that each CPU will sequentially run an equal number of cases (100 in this case). 

set_env_vars=`python3 parse_args.py $@`
eval "$set_env_vars"
source _do_all_config.sh

# Clean up from previous runs
rm -rf $RESULTS_DIR
rm -rf $TMP_DIR

# Split data into batches
apptainer run $CONTAINER_IMAGE split_data.py -nj $ARRAY_SIZE -np $NTASKS_PER_JOB -i $INPUT_FILE --results $RESULTS_DIR --tmp $TMP_DIR

# Run main computations
SUBMIT_CONFIRMATION=`sbatch -A $ACCOUNT --array 1-$ARRAY_SIZE --mem-per-cpu $MEM_PER_CPU --ntasks $NTASKS_PER_JOB --time $WALLTIME _run.sh $@`
JOB_ID=$(echo "$SUBMIT_CONFIRMATION" | grep -o -E '[0-9]+')

# Merge results
sbatch --dependency afterok:$JOB_ID -A $ACCOUNT --mem-per-cpu $MEM_PER_CPU_POST --ntasks 1 --time $WALLTIME_POST _merge_results.sh $@