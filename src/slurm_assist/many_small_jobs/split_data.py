"""
FILE: split_data.py
PURPOSE: Split data into batches and save to files.
DESCRIPTION:
    Will create one chunk of data for each cpu, for each job. For example, suppose the data file 
    contains a list of 24 data entries. If num_jobs=3 and num_proc_per_job=2, then the file tree
    created will be:

        output_dir/
            data_batch_0_0.pkl
            data_batch_0_1.pkl
            data_batch_1_0.pkl
            data_batch_1_1.pkl
            data_batch_2_0.pkl
            data_batch_2_1.pkl

    where each data_batch_i_j.pkl contains 4 data entries. Here, i corresponds to the job array number,
    and j corresponds to the cpu/process number within a job.
"""

import pickle as pkl
import os

def main(
    input_file: str,
    batched_data_dir: str,
    job_array: list[int],
    ntasks_per_job: int,
):
    """Split data into batches and save to files."""
    
    num_jobs = len(job_array)
    
    # Import the data file
    with open(input_file, 'rb') as f:
        data = pkl.load(f)
    
    # Give each data entry a unique ID
    data = list(zip(range(len(data)), data))  # [(id, data), ...]
    
    # Define helper function for chunking the data
    def _split_list(a: list, n: int) -> list[tuple[int, list]]:
        k, m = divmod(len(a), n)
        return [a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n)]
    
    # Split data into batches (1 batch per cpu in the job array)
    data_batches = _split_list(data, num_jobs*ntasks_per_job)  # [[(id, data), ...], ...]

    # Save each data batch to a file
    for k, batch in enumerate(data_batches):
        i = k // ntasks_per_job
        j = k % ntasks_per_job
        data_batch_filepath = os.path.join(batched_data_dir, f'data_{job_array[i]}_{j}.pkl')
        print(f'Saving data batch {job_array[i]}_{j} to {data_batch_filepath} ... ', end='')
        with open(data_batch_filepath, 'wb') as f:
            pkl.dump(batch, f)
        print('done.')
    
    # Return the number of data batches
    return len(data_batches)

# def create_dirs(results_dir: str, tmp_dir: str):
#     data_batch_dir = os.path.join(tmp_dir, 'data_batched')
#     results_batch_dir = os.path.join(tmp_dir, 'results_batched')
#     results_supplemental_dir = os.path.join(results_dir, 'split_results')
#     os.makedirs(data_batch_dir, exist_ok=True)
#     os.makedirs(results_batch_dir, exist_ok=True)
#     os.makedirs(results_supplemental_dir, exist_ok=True)

# if __name__=="__main__":
#     import argparse
#     import time
#     import sys

#     parser = argparse.ArgumentParser()
#     parser.add_argument('-i', '--input-file', type=str)
#     parser.add_argument('--results', type=str)
#     parser.add_argument('--tmp', type=str)
#     parser.add_argument('-nj', '--num-jobs', type=int)
#     parser.add_argument('-np', '--num-proc-per-job', type=int)
#     args = parser.parse_args()

#     print('\nSplitting data into batches...')
#     t1 = time.time()
#     N = main(
#         input_file=args.input_file,
#         results_dir=args.results,
#         tmp_dir=args.tmp,
#         num_jobs=args.num_jobs,
#         num_proc_per_job=args.num_proc_per_job
#     )
#     t2 = time.time()
#     print('...done.')
#     print('Total elapsed time: {:.5f}\n'.format(t2 - t1))