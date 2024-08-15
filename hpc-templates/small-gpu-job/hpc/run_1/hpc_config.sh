#!/bin/bash

NODES=1  # Number of jobs to submit
NTASKS=1  # Number of CPUs per job
GPUS_PER_NODE=1  # Number of CPUs per job
MEM_PER_CPU=2048M  # Memory per CPU
WALLTIME=0:20:00  # Walltime
ACCOUNT=debug  # The queue to submit to