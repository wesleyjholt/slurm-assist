#!/bin/bash

ARRAY_SIZE=2  # Number of jobs to submit
NTASKS_PER_JOB=3  # Number of CPUs per job
MEM_PER_CPU=1024M  # Memory per CPU
WALLTIME=0:30:00  # Walltime

MEM_PER_CPU_MERGE=1024M  # Memory per CPU for post-processing
WALLTIME_MERGE=0:10:00  # Walltime for post-processing

MOVE_RESULTS=1  # Whether to move results to a different directory
MOVE_RESULTS_TO_CLUSTER=gilbreth
MOVE_RESULTS_TO_PATH=/scratch/gilbreth/holtw/example-data-imported-from-bell # Path to move results to
ARRAY_SIZE_MOVE=3  # Number of jobs to submit for moving files
MEM_PER_CPU_MOVE=1024M  # Memory per CPU for moving files
WALLTIME_MOVE=0:10:00  # Walltime for moving files

INPUT_FILE=run_1/data.pkl  # Contains all input data in one giant list.

ACCOUNT=standby  # The queue to submit to