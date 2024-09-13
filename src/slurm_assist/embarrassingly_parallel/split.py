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

def main(
    input_file: str,
    batched_data_dir: str,
    job_array: list[int],
    ntasks_per_job: int,
    generate_new_ids: bool
):
    """Split data into batches and save to files."""
    
    num_jobs = len(job_array)
    
    # Import the data file
    data = load_csv(input_file)
    
    # Give each data entry a unique ID
    if generate_new_ids:
        print('Generating new IDs')
        data = list(zip(range(len(data)), data))  # [(id, data), ...]
    else:
        is_valid_id = list(map(lambda x: str(x[0]).isdigit(), data))
        if not all(is_valid_id):
            raise ValueError('Tried to parse the the first column of the input csv file {input_file} as IDs, but \n \
                             at least one entry is not an integer. Set generate_new_ids=True to generate new IDs.')
        print('Using existing IDs')
        ids = list(map(lambda x: int(x[0]), data))
        data = list(map(lambda x: x[1:], data))
        data = list(zip(ids, data))  # [(id, data), ...]
    
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

if __name__ == '__main__':
    import argparse
    import time
    import sys

    parser = argparse.ArgumentParser(description='Split data into batches and save to files.')
    parser.add_argument('--utils-parent-dir', type=str)
    parser.add_argument('--input-file', type=str, help='Path to the input data file.')
    parser.add_argument('--batched-data-dir', type=str, help='Directory to save the batched data.')
    parser.add_argument('--job-array', type=int, nargs='+', help='Array of job numbers.')
    parser.add_argument('--ntasks-per-job', type=int, default=1, help='Number of tasks per job.')
    parser.add_argument('--generate-new-ids', action='store_true', help='Generate new IDs for the data entries.')
    args, unknown_args = parser.parse_known_args()

    t1 = time.time()
    sys.path.append(args.utils_parent_dir)
    try:
        from utils import load_csv, save_pickle
    except:
        raise Exception('Could not import utils module. Make sure the --parent-dir argument is pointing to the package\'s embarrassingly_parallel directory.')
    main(args.input_file, args.batched_data_dir, args.job_array, args.ntasks_per_job, args.generate_new_ids)
    t2 = time.time()
    print('Elapsed time for splitting data: {:.5f}'.format(t2 - t1))