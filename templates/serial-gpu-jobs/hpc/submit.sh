#!/bin/bash

set_env_vars=`python3 parse_args.py $@`
eval "$set_env_vars"
source _do_all_config.sh

# Clean up from previous runs
rm -rf $RESULTS_DIR
rm -rf $TMP_DIR

# Store sbatch arguments
args="-A $ACCOUNT --nodes $NODES --ntasks $NTASKS --gpus-per-node $GPUS_PER_NODE --mem-per-cpu $MEM_PER_CPU --time $WALLTIME"
if [ "$REQUIRE_SUCCESS" = 1 ]; then
    dependency="--dependency=afterok"
else
    dependency="--dependency=afterany"
fi

# Submit first job
output=$(sbatch $args _run.sh)
echo "$output"
jobid=$(echo "$output" | awk '{print $4}')

# Submit remaining jobs
for ((i=1; i<NUM_SERIAL_JOBS; i++)); do
    output=$(sbatch $args $dependency:$jobid _run.sh)
    echo "$output"
    jobid=$(echo "$output" | awk '{print $4}')
done
