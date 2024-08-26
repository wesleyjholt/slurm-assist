#!/bin/bash

# FILE: submit.sh
# PURPOSE: Submit many independent CPU runs to the HPC to run in parallel.
# DESCRIPTION: 
#     Suppose you have 1,000,000 independent cases to run. With this script, you can
#     e.g., 
#          - submit 100 different jobs (ARRAY_SIZE),
#          - each using 100 different CPUs (NTASKS_PER_JOB)
#          - so that each CPU will sequentially run an equal number of cases (100 in this case). 

echo 1
set_env_vars=`python3 parse_args.py $@`
echo 2
eval "$set_env_vars"
echo 3
source _do_all_config.sh
echo 4

# Clean up from previous runs
rm -rf $RESULTS_DIR
rm -rf $TMP_DIR
echo 5

# Split data into batches
apptainer run $CONTAINER_IMAGE split_data.py -nj $ARRAY_SIZE -np $NTASKS_PER_JOB -i $INPUT_FILE --results $RESULTS_DIR --tmp $TMP_DIR
echo 6

# Run main computations
output=`sbatch -A $ACCOUNT --array 1-$ARRAY_SIZE --mem-per-cpu $MEM_PER_CPU --ntasks $NTASKS_PER_JOB --time $WALLTIME _run.sh $@`
echo "$output"
jobid=$(echo "$output" | awk '{print $4}')
echo 7

# Merge results
output=`sbatch --dependency afterok:$jobid -A $ACCOUNT --mem-per-cpu $MEM_PER_CPU_MERGE --ntasks 1 --time $WALLTIME_MERGE _merge_results.sh $@`
echo "$output"
jobid=$(echo "$output" | awk '{print $4}')
echo 8

# Move results
if [ $MOVE_RESULTS -eq 1 ]; then
    if [ ! -f $SSH_KEY_PATH ]; then
        echo -e $SSH_KEY_PATH'\n\n' | ssh-keygen -f $SSH_KEY_PATH -P ''
        ssh-copy-id -i ${SSH_KEY_PATH}.pub $USERNAME@$MOVE_RESULTS_TO_CLUSTER.rcac.purdue.edu
    fi
    sbatch --dependency afterok:$jobid -A $ACCOUNT --array 1-$ARRAY_SIZE_MOVE --mem-per-cpu $MEM_PER_CPU_MOVE --ntasks 1 --time $WALLTIME_MOVE _move_results.sh $@
fi