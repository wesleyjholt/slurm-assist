"""
FILE: merge_results.py
PURPOSE: Merge results from many independent CPU runs.
DESCRIPTION:
    This script saves a list with the results for each case. The entries of the list can either 
    be the results themselves, or filepaths to the results.
"""

import os
import pandas as pd
import subprocess
from typing import *

def main(
    batched_results_dir: str,
    merged_results_file: str,
    tmp_dir: str,
    job_array: int,
    ntasks_per_job: int
):
    """Collect/merge the results."""
    job_array_ = parse_slurm_array(job_array)

    # Collect results for each batch of computation and append to a single list.
    num_jobs = len(job_array_)
    results = []
    for k in range(num_jobs*ntasks_per_job):
        i = k // ntasks_per_job
        j = k % ntasks_per_job
        results_batch_file = os.path.join(batched_results_dir, f'results_{job_array_[i]}_{j}.pkl')
        try:
            res_ij = load_pickle(results_batch_file)
            for res_ijl in res_ij:
                results.append(res_ijl)
            print(f'Loaded {results_batch_file}')
            
        except:
            print(f'Failed to load {results_batch_file}')
    
    # Save results to a single file
    # save_csv(results, merged_results_file)
    pd.DataFrame(results).to_csv(merged_results_file, index=False, header=False)

    # Delete tmp files
    subprocess.run(['rm', '-rf', tmp_dir])
        

if __name__=='__main__':
    import argparse
    import time
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument('--utils-parent-dir', '--utils_parent_dir', type=str)
    parser.add_argument('--batched-results-dir', '--batched_results_dir', type=str)
    parser.add_argument('--merged-results-file', '--merged_results_file', type=str)
    parser.add_argument('--tmp-dir', '--tmp_dir', type=str)
    parser.add_argument('--job-array', '--job_array', type=str)
    parser.add_argument('--ntasks-per-job', '--ntasks_per_job', type=int)
    args = parser.parse_args()

    print('\nMerging results...')
    t1 = time.time()
    sys.path.append(args.utils_parent_dir)
    try:
        from utils import load_pickle, save_csv, parse_slurm_array
    except:
        raise Exception('Could not import utils module. Make sure the --parent-dir argument is pointing to the package\'s many_small_jobs_directory.')
    main(
        batched_results_dir=args.batched_results_dir,
        merged_results_file=args.merged_results_file,
        tmp_dir=args.tmp_dir,
        job_array=args.job_array,
        ntasks_per_job=args.ntasks_per_job
    )
    t2 = time.time()
    print('...done.')
    print('Elapsed time for merging results: {:.5f}'.format(t2 - t1))