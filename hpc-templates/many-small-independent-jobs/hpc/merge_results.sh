#!/bin/bash

# Check input arguments
if [ -z "$1" ]; then
  echo "Error: No run name provided."
  echo "Usage: $0 <RUN_NAME>"
  exit 1
fi

# Set up environment
export RUN_NAME=$1
source _do_all_config.sh

source _merge_results.sh