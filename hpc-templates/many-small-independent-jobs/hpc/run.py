"""
FILE: run.py
PURPOSE: Run a batches data through user-defined processing.
"""

import os
import pickle as pkl
import importlib
from mpi4py import MPI

run_single = importlib.import_module(f"{os.environ['RUN_NAME']}.run_single").run_single
    
def main(
    job_id: int, 
    results_dir: str,
    tmp_dir: str
):
    """Main entry point.

    Note that job_id is the job array task ID, not the SLURM job ID.
    """
    rank = MPI.COMM_WORLD.rank
    data_batch_dir = os.path.join(tmp_dir, 'data_batch')
    results_batch_dir = os.path.join(tmp_dir, 'results_batch')
    results_supplemental_dir = os.path.join(results_dir, 'results_supplemental')
    _run(job_id, rank, data_batch_dir, results_batch_dir, results_supplemental_dir)

def _run(
    job_id: int, 
    batch_id: int,
    data_batch_dir: str,
    results_batch_dir: str,
    results_supplemental_dir: str
):
    # Load data batch
    data_batch_filepath = os.path.join(data_batch_dir, f'{job_id}_{batch_id}.pkl')
    with open(data_batch_filepath, 'rb') as f:
        ids_and_data_batch = pkl.load(f)
    if len(ids_and_data_batch) == 0:
        result = []
        ids = []
    else:
        ids, data_batch = list(zip(*ids_and_data_batch))  # unzip

        # Run the batch through processing
        result = _run_batch(ids, data_batch, results_supplemental_dir)
    
    # Save results
    results_batch_filepath = os.path.join(results_batch_dir, f'{job_id}_{batch_id}.pkl')
    os.makedirs(results_batch_dir, exist_ok=True)
    with open(results_batch_filepath, 'wb') as f:
        pkl.dump(list(zip(ids, result)), f)

def _run_batch(
    run_ids: int,
    data_batch: list,
    results_supplemental_dir: str
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
        results.append(run_single(id, data, results_supplemental_dir))
    return results


if __name__=='__main__':
    import argparse
    import time

    parser = argparse.ArgumentParser()
    parser.add_argument('--job-id', type=str)
    parser.add_argument('--results', type=str)
    parser.add_argument('--tmp', type=str)
    args = parser.parse_args()

    t1 = time.time()
    main(
        job_id=args.job_id, 
        results_dir=args.results,
        tmp_dir=args.tmp
    )
    t2 = time.time()
    print('Total run time: {:.5f}'.format(t2 - t1))