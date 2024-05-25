## USER MUST EDIT THIS FILE
USERNAME=holtw
CLUSTER=bell
PATH_TO_REMOTE=/scratch/${CLUSTER}/${USERNAME}/many_independent_cpu_runs/

# create path to remote if it deosn't exist
ssh ${USERNAME}@${CLUSTER}.rcac.purdue.edu "mkdir -p ${PATH_TO_REMOTE}"

scp -r ./ ${USERNAME}@${CLUSTER}.rcac.purdue.edu:${PATH_TO_REMOTE}