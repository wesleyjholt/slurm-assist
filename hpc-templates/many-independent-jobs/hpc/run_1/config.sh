#!/bin/bash

ARRAY_SIZE=2  # Number of jobs to submit
NTASKS_PER_JOB=3  # Number of CPUs per job
MEM_PER_CPU=2048M  # Memory per CPU
WALLTIME=4:00:00  # Walltime
MEM_PER_CPU_POST=1028M  # Memory per CPU for post-processing
WALLTIME_POST=0:10:00  # Walltime for post-processing
INPUT_FILE=hpc/run_1/data.pkl  # Contains all input data in one giant list.
ENVIRONMENT=myenv-py3.11.7  # Conda environment to load
ACCOUNT=standby  # The queue to submit to