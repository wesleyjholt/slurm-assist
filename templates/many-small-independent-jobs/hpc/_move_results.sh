#!/bin/bash

#SBATCH --job-name=move_results

# Set up environment
source _do_all_config.sh
module purge

# Set up tracking
module load utilities monitor
monitor cpu percent >cpu-percent-run.log &
CPU_PID=$!

# Get the files to move
apptainer run $CONTAINER_IMAGE split_files.py --directories $RESULTS_DIR --N $ARRAY_SIZE_MOVE --tmp $TMP_DIR

# Move files
ssh -i $SSH_KEY_PATH $USERNAME@$MOVE_RESULTS_TO_CLUSTER.rcac.purdue.edu "mkdir -p $MOVE_RESULTS_TO_PATH"
files_from=results_filenames_$(($SLURM_ARRAY_TASK_ID - 1)).txt
# Fix tmpdir/filesfrom
rsync -avx --no-times --progress -e "ssh -i $SSH_KEY_PATH" --files-from=$TMP_DIR/$files_from ./ $USERNAME@$MOVE_RESULTS_TO_CLUSTER.rcac.purdue.edu:$MOVE_RESULTS_TO_PATH

# # Run computations
# apptainer run $CONTAINER_IMAGE run.py --job-id $(($SLURM_ARRAY_TASK_ID - 1)) --results $RESULTS_DIR --tmp $TMP_DIR

# Shut down the resource monitors
kill -s INT $CPU_PID