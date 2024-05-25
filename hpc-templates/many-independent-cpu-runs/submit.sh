#!/bin/bash

# FILE: submit_many.sh
# PURPOSE: Submit many independent CPU runs to the HPC to run in parallel.
# DESCRIPTION: 
#     Suppose you have 1,000,000 independent cases to run. With this script, you can
#     e.g., 
#          - submit 100 different jobs (ARRAY_SIZE),
#          - each using 100 different CPUs (NTASKS_PER_JOB)
#          - so that each CPU will sequentially run an equal number of cases (100 in this case). 

# ==== User inputs ==== #
ARRAY_SIZE=3  # Number of jobs to submit
NTASKS_PER_JOB=5  # Number of CPUs per job
MEM_PER_CPU=512M  # Memory per CPU
MEM_PER_CPU_POST=512M  # Memory per CPU for post-processing
INPUT_FILE=input_data.pkl  # Contains all input data in one giant list.
BATCHED_DATA_DIR=data_batches  # Directory to store batched data 
BATCHED_RESULTS_DIR=results_batches  # Directory to store batched results
OUTPUT_FILE=results.pkl  # File to store results
ENVIRONMENT=myenv-py3.11.7  # Conda environment to load
# ===================== #

# Clean up from previous runs
rm -rf $BATCHED_DATA_DIR
rm -rf $BATCHED_RESULTS_DIR

# Load environment
module load use.own
module load conda-env/$ENVIRONMENT

# Split data into batches
python3 split_data.py -nj $ARRAY_SIZE -np $NTASKS_PER_JOB -i $INPUT_FILE -o $BATCHED_DATA_DIR

# Run main computations
SUBMIT_CONFIRMATION=`sbatch --array 1-$ARRAY_SIZE --mem-per-cpu $MEM_PER_CPU --ntasks $NTASKS_PER_JOB _run.sh $BATCHED_DATA_DIR $BATCHED_RESULTS_DIR $OUTPUT_FILE $METADATA_FILE $ENVIRONMENT`
JOB_ID=$(echo "$SUBMIT_CONFIRMATION" | grep -o -E '[0-9]+')

# Merge results
sbatch --dependency afterok:$JOB_ID --mem-per-cpu $MEM_PER_CPU_POST --ntasks 1 _merge_results.sh $ARRAY_SIZE $NTASKS_PER_JOB $BATCHED_RESULTS_DIR $OUTPUT_FILE $ENVIRONMENT