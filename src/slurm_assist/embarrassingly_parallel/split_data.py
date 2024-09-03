"""
FILE: split_data.py
PURPOSE: Split data into batches and save to files.
DESCRIPTION:
    Will create one chunk of data for each cpu, for each job. For example, suppose the data file 
    contains a list of 24 data entries. If num_jobs=3 and num_proc_per_job=2, then the file tree
    created will be:

        output_dir/
            data_batch_0_0.txt
            data_batch_0_1.txt
            data_batch_1_0.txt
            data_batch_1_1.txt
            data_batch_2_0.txt
            data_batch_2_1.txt

    where each data_batch_i_j.txt contains 4 data entries. Here, i corresponds to the job array number,
    and j corresponds to the cpu/process number within a job.
"""

import os
from ..utils import load_csv, save_pickle

def main(
    input_file: str,
    batched_data_dir: str,
    job_array: list[int],
    ntasks_per_job: int,
):
    """Split data into batches and save to files."""
    
    num_jobs = len(job_array)
    
    # Import the data file
    data = load_csv(input_file)
    
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
        save_pickle(batch, data_batch_filepath)
        print('done.')
    
    # Return the number of data batches
    return len(data_batches)
