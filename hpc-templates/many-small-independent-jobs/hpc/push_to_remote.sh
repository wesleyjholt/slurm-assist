#!/bin/bash

set_env_vars=`python3 parse_args.py $@`
eval "$set_env_vars"
source hpc_config_global.sh

PATH_TO_REMOTE=/scratch/${CLUSTER}/${USERNAME}/${PROJECT_NAME}/v${CODE_VERSION}

# Create path to remote if it doesn't exist
ssh ${USERNAME}@${CLUSTER}.rcac.purdue.edu "mkdir -p ${PATH_TO_REMOTE}"

FILES=`python3 get_files_to_push.py --project-root-dir $PROJECT_ROOT_DIR --run-name $RUN_NAME --ignore-patterns results/`
echo The following files will be pushed to $PATH_TO_REMOTE on the remote machine:
echo $FILES
echo $FILES \
| xargs tar cf - \
| ssh ${USERNAME}@${CLUSTER}.rcac.purdue.edu tar xf - -C ${PATH_TO_REMOTE}