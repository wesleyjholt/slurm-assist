"""
FILE: merge_results.py
PURPOSE: Merge results from many independent CPU runs.
DESCRIPTION:
    This script saves a list with the results for each case. The entries of the list can either 
    be the results themselves, or filepaths to the results.
"""

import os
import pickle as pkl
from typing import *
from numpy.typing import *

def main(
    input_dir: str,
    output_file: str,
    num_jobs: int,
    num_proc_per_job: int
):
    """Collect/merge the results."""
    # Collect results for each batch of computation and append to a single list.
    results = []
    for k in range(num_jobs*num_proc_per_job):
        i = k // num_proc_per_job
        j = k % num_proc_per_job
        results_batch_filepath = os.path.join(input_dir, f'results_{i}_{j}.pkl')
        try:
            with open(results_batch_filepath, 'rb') as f:
                res_ij = pkl.load(f)
            for res_ijl in res_ij:
                results.append(res_ijl)
                print('res_ijl:', res_ijl)
            print(f'Loaded results_{i}_{j}.pkl')
            
        except:
            print(f'Failed to load results_{i}_{j}.pkl')
    
    # Save results to a single file
    with open(output_file, 'wb') as f:
        pkl.dump(results, f)
        

if __name__=='__main__':
    import argparse
    import time

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-dir', type=str)
    parser.add_argument('-o', '--output-file', type=str)
    parser.add_argument('-nj', '--num-jobs', type=int)
    parser.add_argument('-np', '--num-proc-per-job', type=int)
    args = vars(parser.parse_args())

    print('\nMerging results...')
    t1 = time.time()
    main(
        input_dir=args['input_dir'],
        output_file=args['output_file'],
        num_jobs=args['num_jobs'],
        num_proc_per_job=args['num_proc_per_job']
    )
    t2 = time.time()
    print('...done.')
    print('Total elapsed time: {:.5f}'.format(t2 - t1))