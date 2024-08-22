#!/bin/bash

ARRAY_SIZE=2  # Number of jobs to submit
NTASKS_PER_JOB=3  # Number of CPUs per job
MEM_PER_CPU=1024M  # Memory per CPU
WALLTIME=0:30:00  # Walltime
MEM_PER_CPU_POST=1024M  # Memory per CPU for post-processing
WALLTIME_POST=0:10:00  # Walltime for post-processing
INPUT_FILE=run_1/data.pkl  # Contains all input data in one giant list.
ACCOUNT=standby  # The queue to submit to