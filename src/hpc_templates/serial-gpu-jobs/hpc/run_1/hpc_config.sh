#!/bin/bash

NODES=1  # Number of jobs to submit
NTASKS=1  # Number of CPUs per job
GPUS_PER_NODE=1  # Number of CPUs per job
MEM_PER_CPU=1024M  # Memory per CPU
WALLTIME=0:03:00  # Walltime
ACCOUNT=standby  # The queue to submit to
NUM_SERIAL_JOBS=3  # Number of serial jobs to submit
REQUIRE_SUCCESS=0  # Whether to require the previous job to succeed before submitting the next job
RUN_ARGS_FILE=run_args  # Path to a file containing arguments to pass to the job script