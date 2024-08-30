"""
FILE: run.py
PURPOSE: Run a batches data through user-defined processing.
"""

import os
import pickle as pkl
from typing import Callable
from mpi4py import MPI
from .utils import load_pickle, save_pickle

def main(
    array_id: int, 
    single_run_fn: Callable[[int, list[str], str], list[str]],
    batched_data_dir: str,
    batched_results_dir: str,
    split_results_dir: str,
    job_array: list[int]
):
    """Main entry point.

    Note that array_id is the job array task ID, not the SLURM job ID.
    """
    batch_id = MPI.COMM_WORLD.rank
    print('here')

    # Load data batch
    data_batch_filepath = os.path.join(batched_data_dir, f'data_{job_array[array_id]}_{batch_id}.pkl')
    ids_and_data_batch = load_pickle(data_batch_filepath)
    if len(ids_and_data_batch) == 0:
        result = []
        ids = []
    else:
        ids, data_batch = list(zip(*ids_and_data_batch))  # unzip

        # Run the batch through processing
        result = _run_batch(single_run_fn, ids, data_batch, split_results_dir)
    
    # Save results
    results_batch_filepath = os.path.join(batched_results_dir, f'results_{job_array[array_id]}_{batch_id}.pkl')
    os.makedirs(batched_results_dir, exist_ok=True)
    save_pickle(list(zip(ids, result)), results_batch_filepath)

def _run_batch(
    single_run_fn: Callable[[int, list[str], str], list[str]],
    run_ids: int,
    data_batch: list,
    split_results_dir: str
):
    """Run a batch of data through user-defined processing.

    Returns a list of same length as `data_batch` containing the result for each batch.
    
    Parameters
    ----------
    mpi_comm: MPI communicator
    job_id: int
        Job array rask ID
    batch_id: int
    data_batch: list
        List of data to run
    
    Returns
    -------
    results: list
        List of results
    """
    results = []
    for id, data in zip(run_ids, data_batch):
        results.append(single_run_fn(id, data, split_results_dir))
    return results


if __name__=='__main__':
    import argparse
    import time

    parser = argparse.ArgumentParser()
    parser.add_argument('--job-id', type=str)
    parser.add_argument('--single-run-fn', type=str)
    parser.add_argument('--batched-data-dir', type=str)
    parser.add_argument('--batched-results-dir', type=str)
    parser.add_argument('--split-results-dir', type=str)
    parser.add_argument('--job-array', type=str)
    args, unknown_args = parser.parse_known_args()

    t1 = time.time()
    main(
        job_id=args.job_id, 
        single_run_fn=args.single_run_fn,
        batched_data_dir=args.batched_data_dir,
        batched_results_dir=args.batched_results_dir,
        split_results_dir=args.split_results_dir,
        job_array=args.job_array
    )
    t2 = time.time()
    print('Total run time: {:.5f}'.format(t2 - t1))