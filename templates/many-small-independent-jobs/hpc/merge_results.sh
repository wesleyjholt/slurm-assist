#!/bin/bash

set_env_vars=`python3 parse_args.py $@`
eval "$set_env_vars"
source _do_all_config.sh
source _merge_results.sh