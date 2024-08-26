#!/bin/bash

set_env_vars=`python3 parse_args.py $@`
eval "$set_env_vars"
source _do_all_config.sh

# Move results
if [ $MOVE_RESULTS -eq 1 ]; then
    if [ ! -f $SSH_KEY_PATH ]; then
        echo -e $SSH_KEY_PATH'\n\n' | ssh-keygen
        ssh-copy-id -i ${SSH_KEY_PATH}.pub $USERNAME@$MOVE_RESULTS_TO_CLUSTER.rcac.purdue.edu
    fi
    apptainer run $CONTAINER_IMAGE split_files.py --directories $RESULTS_DIR --N $ARRAY_SIZE_MOVE --tmp $TMP_DIR
    ssh $USERNAME@$MOVE_RESULTS_TO_HOST "mkdir -p $MOVE_RESULTS_TO_PATH"
    sbatch --dependency afterok:$jobid -A $ACCOUNT --array 1-$ARRAY_SIZE_MOVE --mem-per-cpu $MEM_PER_CPU_MOVE --ntasks 1 --time $WALLTIME_MOVE _move_results.sh $@
fi