source hpc/config.sh

if [ -z "$1" ]; then
  echo "Error: No run name provided."
  echo "Usage: $0 <RUN_NAME>"
  exit 1
fi

export RUN_NAME=$1

PATH_TO_REMOTE=/scratch/${CLUSTER}/${USERNAME}/${PROJECT_NAME}/v${CODE_VERSION}/hpc/${RUN_NAME}/results.pkl
PATH_TO_LOCAL=./hpc/${RUN_NAME}

scp ${USERNAME}@${CLUSTER}.rcac.purdue.edu:${PATH_TO_REMOTE} $PATH_TO_LOCAL