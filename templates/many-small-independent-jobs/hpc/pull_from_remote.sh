#!/bin/bash

set_env_vars=`python3 parse_args.py $@`
eval "$set_env_vars"
source _do_all_config.sh

current_dir=$(pwd)
parent_dir=$(realpath $PROJECT_ROOT_DIR)
RELATIVE_PATH_TO_HPC_DIR=${current_dir#$parent_dir/}

PATH_TO_REMOTE=/scratch/${CLUSTER}/${USERNAME}/${PROJECT_NAME}/v${CODE_VERSION}/${RELATIVE_PATH_TO_HPC_DIR}/${RUN_NAME}
PATH_TO_LOCAL=./${RUN_NAME}

# Pull results to local machine
if [ "$PULL_SUPPLEMENTAL" = 1 ]; then
    ssh ${USERNAME}@${CLUSTER}.rcac.purdue.edu "tar cf - -C ${PATH_TO_REMOTE} results" | tar xf - -C ${PATH_TO_LOCAL}
else
    ssh ${USERNAME}@${CLUSTER}.rcac.purdue.edu "tar cf - -C ${PATH_TO_REMOTE} results/results.pkl" | tar xf - -C ${PATH_TO_LOCAL}
fi