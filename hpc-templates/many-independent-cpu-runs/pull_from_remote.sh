USERNAME=holtw
CLUSTER=bell
PATH_TO_REMOTE=/scratch/${CLUSTER}/${USERNAME}/many-independent-cpu-runs/results.pkl
PATH_TO_LOCAL=./

scp ${USERNAME}@${CLUSTER}.rcac.purdue.edu:${PATH_TO_REMOTE} $PATH_TO_LOCAL