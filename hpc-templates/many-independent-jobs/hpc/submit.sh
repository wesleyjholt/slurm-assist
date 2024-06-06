#!/bin/bash

# FILE: submit_many.sh
# PURPOSE: Submit many independent CPU runs to the HPC to run in parallel.
# DESCRIPTION: 
#     Suppose you have 1,000,000 independent cases to run. With this script, you can
#     e.g., 
#          - submit 100 different jobs (ARRAY_SIZE),
#          - each using 100 different CPUs (NTASKS_PER_JOB)
#          - so that each CPU will sequentially run an equal number of cases (100 in this case). 

if [ -z "$1" ]; then
  echo "Error: No run name provided."
  echo "Usage: $0 <RUN_NAME>"
fi

export RUN_NAME=$1
export HPC_DIR=hpc
export BATCHED_DATA_DIR=${HPC_DIR}/${RUN_NAME}/data_batches  # Directory to store batched data 
export BATCHED_RESULTS_DIR=${HPC_DIR}/${RUN_NAME}/results_batches  # Directory to store batched results
export OUTPUT_FILE=${HPC_DIR}/${RUN_NAME}/results.pkl  # File to store results

source ${HPC_DIR}/config.sh
source ${HPC_DIR}/${RUN_NAME}/config.sh

# Clean up from previous runs
rm -rf $BATCHED_DATA_DIR
rm -rf $BATCHED_RESULTS_DIR

# Load environment
module load use.own
module load conda-env/$ENVIRONMENT

# Split data into batches
python3 -m ${HPC_DIR}.split_data -nj $ARRAY_SIZE -np $NTASKS_PER_JOB -i $INPUT_FILE -o $BATCHED_DATA_DIR

# Run main computations
SUBMIT_CONFIRMATION=`sbatch -A $ACCOUNT --array 1-$ARRAY_SIZE --mem-per-cpu $MEM_PER_CPU --ntasks $NTASKS_PER_JOB --time $WALLTIME ${HPC_DIR}/_run.sh`
JOB_ID=$(echo "$SUBMIT_CONFIRMATION" | grep -o -E '[0-9]+')

# Merge results
sbatch --dependency afterok:$JOB_ID -A $ACCOUNT --mem-per-cpu $MEM_PER_CPU_POST --ntasks 1 --time $WALLTIME_POST ${HPC_DIR}/_merge_results.sh