# How to run a many small independent jobs

### 1. Navigate to `hpc` directory.
```bash
cd hpc
```

### 2. Edit configuration files.
```bash
# Edit the global configuration file
nano hpc_config_global.sh

# Set the name of your run
# (there should already exist a directory with this name)
RUN_NAME=run_1

# Edit the configuration file for your run
nano $RUN_NAME/hpc_config.sh
```

### 3. Move files to remote machine.
```bash
# Set the root directory of your project
PROJECT_ROOT_DIR=../

# Create/modify the .hpc-ignore file (optional)
# This file prevents moving unwanted files/directories to the remote cluster. 
# It has the same format as a .gitignore file.
nano $PROJECT_ROOT_DIR/.hpc-ignore

# Move files to remote machine
source push_to_remote.sh --run-name $RUN_NAME --project-root-dir $PROJECT_ROOT_DIR
```

### 4. Log into remote cluster.
```bash
ssh <username>@<remote_machine>
```

### 5. Build the container.
```bash
### In remote machine ###

# Navigate to hpc file (as set in hpc_config_global.sh)
cd path/to/hpc

# Change to the name of your container definition file
CONTAINER_DEF=jax-mpi.def  

# Change to the name of the container image (as set in hpc_config_global.sh)
CONTAINER_IMAGE=jax-mpi.sif

# Build container
apptainer build $CONTAINER_IMAGE $CONTAINER_DEF
```

### 6. Submit the job.
```bash
# Set the name of your run
RUN_NAME=run_1

# Submit the job
source submit.sh --run-name $RUN_NAME
```

### 7. Pull results to local machine (once job is finished).
```bash
### Back in local machine ###
source pull_from_remote.sh --run-name $RUN_NAME --project-root-directory $PROJECT_ROOT_DIR  --pull-supplementary

# Note: Leave out the `--pull-supplementary` flag if you don't want to pull supplementary files.
```

- **Note:** If any of the jobs fail, you can still merge all the results together by running `source hpc/merge_results.sh <run_name>`. You will also need to cancel `merge_results` job by running `scancel <job_id>`. Again, this is only necessary if a job fails.

- **TODO:** 
    - Merge results automatically if any job fails.
    - For a batch where some runs fail, allow the non-failed runs to still be merged with the rest of the results.