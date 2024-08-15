"""
FILE: merge_results.py
PURPOSE: Merge results from many independent CPU runs.
DESCRIPTION:
    This script saves a list with the results for each case. The entries of the list can either 
    be the results themselves, or filepaths to the results.
"""

import os
import pickle as pkl
import csv
from typing import *
from numpy.typing import *

def main(
    results_dir: str,
    tmp_dir: str,
    num_jobs: int,
    num_proc_per_job: int
):
    """Collect/merge the results."""
    # Collect results for each batch of computation and append to a single list.
    results_batch_dir = os.path.join(tmp_dir, 'results_batch')
    results = []
    for k in range(num_jobs*num_proc_per_job):
        i = k // num_proc_per_job
        j = k % num_proc_per_job
        results_batch_filepath = os.path.join(results_batch_dir, f'{i}_{j}.pkl')
        try:
            with open(results_batch_filepath, 'rb') as f:
                res_ij = pkl.load(f)
            for res_ijl in res_ij:
                results.append(res_ijl)
            print(f'Loaded {results_batch_filepath}')
            
        except:
            print(f'Failed to load {results_batch_filepath}')
    
    # Save results to a single file
    output_file = os.path.join(results_dir, 'results.pkl')
    with open(output_file, 'wb') as f:
        pkl.dump(results, f)
        

if __name__=='__main__':
    import argparse
    import time

    parser = argparse.ArgumentParser()
    parser.add_argument('--results', type=str)
    parser.add_argument('--tmp', type=str)
    parser.add_argument('-nj', '--num-jobs', type=int)
    parser.add_argument('-np', '--num-proc-per-job', type=int)
    args = parser.parse_args()

    print('\nMerging results...')
    t1 = time.time()
    main(
        results_dir=args.results,
        tmp_dir=args.tmp,
        num_jobs=args.num_jobs,
        num_proc_per_job=args.num_proc_per_job
    )
    t2 = time.time()
    print('...done.')
    print('Total elapsed time: {:.5f}'.format(t2 - t1))