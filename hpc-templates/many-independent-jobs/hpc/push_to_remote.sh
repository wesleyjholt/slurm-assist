source hpc/config.sh

PATH_TO_REMOTE=/scratch/${CLUSTER}/${USERNAME}/${PROJECT_NAME}/v${CODE_VERSION}

# Create path to remote if it doesn't exist
ssh ${USERNAME}@${CLUSTER}.rcac.purdue.edu "mkdir -p ${PATH_TO_REMOTE}"

scp -r ./ ${USERNAME}@${CLUSTER}.rcac.purdue.edu:${PATH_TO_REMOTE}