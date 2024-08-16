#!/bin/bash

# Check input arguments
USAGE_HINT="Usage: $0 <run_name> <project-root-dir>"
if [ -z "$1" ]; then
  echo "Error: No run name provided."
  echo $USAGE_HINT
fi
if [ -z "$2" ]; then
  echo "Error: No project root directory provided."
  echo $USAGE_HINT
fi

# Set up environment
export RUN_NAME=$1
export PROJECT_ROOT_DIR=$2
source _do_all_config.sh

current_dir=$(pwd)
parent_dir=$(realpath $PROJECT_ROOT_DIR)
RELATIVE_PATH_TO_HPC_DIR=${current_dir#$parent_dir/}

PATH_TO_REMOTE=/scratch/${CLUSTER}/${USERNAME}/${PROJECT_NAME}/v${CODE_VERSION}/${RELATIVE_PATH_TO_HPC_DIR}/${RUN_NAME}
PATH_TO_LOCAL=./${RUN_NAME}

# Pull results to local machine
ssh ${USERNAME}@${CLUSTER}.rcac.purdue.edu "tar cf - -C ${PATH_TO_REMOTE} results" | tar xf - -C ${PATH_TO_LOCAL}