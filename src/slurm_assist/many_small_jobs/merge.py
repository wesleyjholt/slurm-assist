"""
FILE: merge_results.py
PURPOSE: Merge results from many independent CPU runs.
DESCRIPTION:
    This script saves a list with the results for each case. The entries of the list can either 
    be the results themselves, or filepaths to the results.
"""

import os
import subprocess
from typing import *
import pickle
import csv
# from .utils import load_pickle, save_csv

def load_pickle(file_path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)

def save_csv(obj, file_path):
    with open(file_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(obj)

def main(
    batched_results_dir: str,
    merged_results_file: str,
    tmp_dir: str,
    job_array: int,
    ntasks_per_job: int
):
    """Collect/merge the results."""
    # Collect results for each batch of computation and append to a single list.
    num_jobs = len(job_array)
    results = []
    for k in range(num_jobs*ntasks_per_job):
        i = k // ntasks_per_job
        j = k % ntasks_per_job
        results_batch_file = os.path.join(batched_results_dir, f'{job_array[i]}_{j}.pkl')
        try:
            res_ij = load_pickle(results_batch_file)
            for res_ijl in res_ij:
                results.append(res_ijl)
            print(f'Loaded {results_batch_file}')
            
        except:
            print(f'Failed to load {results_batch_file}')
    
    # Save results to a single file
    save_csv(results, merged_results_file)

    # Delete tmp files
    subprocess.run(['rm', '-rf', tmp_dir])
        

if __name__=='__main__':
    import argparse
    import time

    parser = argparse.ArgumentParser()
    parser.add_argument('--batched-results-dir', type=str)
    parser.add_argument('--merged-results-file', type=str)
    parser.add_argument('--tmp-dir', type=str)
    parser.add_argument('--job-array', type=int)
    parser.add_argument('--ntasks-per-job', type=int)
    args = parser.parse_args()

    print('\nMerging results...')
    t1 = time.time()
    main(
        batched_results_dir=args.batched_results_dir,
        merged_results_file=args.merged_results_file,
        tmp_dir=args.tmp_dir,
        job_array=args.job_array,
        ntasks_per_job=args.ntasks_per_job
    )
    t2 = time.time()
    print('...done.')
    print('Total elapsed time: {:.5f}'.format(t2 - t1))