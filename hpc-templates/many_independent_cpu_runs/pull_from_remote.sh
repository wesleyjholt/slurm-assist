USERNAME=holtw
CLUSTER=bell
PATH_TO_REMOTE=/scratch/${CLUSTER}/${USERNAME}/many_independent_cpu_runs/results.pkl
PATH_TO_LOCAL=./

scp ${USERNAME}@${CLUSTER}.rcac.purdue.edu:${PATH_TO_REMOTE} $PATH_TO_LOCAL