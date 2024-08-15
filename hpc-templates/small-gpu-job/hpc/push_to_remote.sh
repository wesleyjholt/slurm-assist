#!/bin/bash

# Check input arguments
if [ -z "$1" ]; then
  echo "Error: No project root directory provided."
  echo "Usage: $0 <project-root-dir>"
  exit 1
fi

# Set up environment
export PROJECT_ROOT_DIR=$1
source hpc_config_global.sh

PATH_TO_REMOTE=/scratch/${CLUSTER}/${USERNAME}/${PROJECT_NAME}/v${CODE_VERSION}

# Create path to remote if it doesn't exist
ssh ${USERNAME}@${CLUSTER}.rcac.purdue.edu "mkdir -p ${PATH_TO_REMOTE}"

# Push files to remote machine
if [ -f "$PROJECT_ROOT_DIR/.hpc-ignore" ]; then
    FILES=$(find $PROJECT_ROOT_DIR -type f | grep -vF -f $PROJECT_ROOT_DIR/.hpc-ignore)
    echo The following files will be pushed to the remote:
    echo $FILES
    echo $FILES \
    | xargs tar cf - \
    | ssh ${USERNAME}@${CLUSTER}.rcac.purdue.edu tar xf - -C ${PATH_TO_REMOTE}
else
    FILES=$(find $PROJECT_ROOT_DIR -type f | grep -v '^.$')
    echo The following files will be pushed to the remote:
    echo $FILES
    echo $FILES \
    | xargs tar cf - \
    | ssh ${USERNAME}@${CLUSTER}.rcac.purdue.edu tar xf - -C ${PATH_TO_REMOTE}
fi