source hpc/config.sh

PATH_TO_REMOTE=/scratch/${CLUSTER}/${USERNAME}/${PROJECT_NAME}/v${CODE_VERSION}

# Create path to remote if it doesn't exist
ssh ${USERNAME}@${CLUSTER}.rcac.purdue.edu "mkdir -p ${PATH_TO_REMOTE}"

if [ -f "hpc-ignore" ]; then
    # Exclude files listed in hpc-ignore
    find . | grep -v '^.$' | grep -v -f hpc-ignore \
    | xargs tar cf - \
    | ssh ${USERNAME}@${CLUSTER}.rcac.purdue.edu tar xf - -C ${PATH_TO_REMOTE}
else
    find . \
    | xargs tar cf - \
    | ssh ${USERNAME}@${CLUSTER}.rcac.purdue.edu tar xf - -C ${PATH_TO_REMOTE}
fi