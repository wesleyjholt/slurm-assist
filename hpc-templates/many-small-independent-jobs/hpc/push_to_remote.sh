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
source hpc_config_global.sh

PATH_TO_REMOTE=/scratch/${CLUSTER}/${USERNAME}/${PROJECT_NAME}/v${CODE_VERSION}

# Create path to remote if it doesn't exist
ssh ${USERNAME}@${CLUSTER}.rcac.purdue.edu "mkdir -p ${PATH_TO_REMOTE}"

FILES=`python3 get_files_to_push.py --project-root-dir $PROJECT_ROOT_DIR --run-name $RUN_NAME --ignore-patterns results/`
echo The following files will be pushed to the remote:
echo $FILES
echo $FILES \
| xargs tar cf - \
| ssh ${USERNAME}@${CLUSTER}.rcac.purdue.edu tar xf - -C ${PATH_TO_REMOTE}