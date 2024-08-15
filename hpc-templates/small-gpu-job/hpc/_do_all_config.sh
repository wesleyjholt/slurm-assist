#!/bin/bash

# Set all necessary variables for the run

export RESULTS_DIR=${RUN_NAME}/results  # Directory to store results
export TMP_DIR=${RUN_NAME}/tmp  # Directory to store temporary files

source hpc_config_global.sh
source ${RUN_NAME}/hpc_config.sh