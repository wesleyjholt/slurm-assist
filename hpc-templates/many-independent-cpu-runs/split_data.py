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
    output_dir: str,
    num_jobs: int,
    num_proc_per_job: int,
):
    """Split data into batches and save to files."""
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
    data_batches = _split_list(data, num_jobs*num_proc_per_job)  # [[(id, data), ...], ...]

    # Save each data batch to a file
    os.makedirs(output_dir, exist_ok=True)
    for k, batch in enumerate(data_batches):
        i = k // num_proc_per_job
        j = k % num_proc_per_job
        data_batch_filepath = os.path.join(output_dir, f'data_batch_{i}_{j}.pkl')
        print(f'Saving data batch {i}_{j} to {data_batch_filepath} ... ', end='')
        with open(data_batch_filepath, 'wb') as f:
            pkl.dump(batch, f)
        print('done.')
    
    # Return the number of data batches
    return len(data_batches)


if __name__=="__main__":
    import argparse
    import time
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-file', type=str)
    parser.add_argument('-o', '--output-dir', type=str)
    parser.add_argument('-nj', '--num-jobs', type=int)
    parser.add_argument('-np', '--num-proc-per-job', type=int)
    args = vars(parser.parse_args())

    print('\nSplitting data into batches...')
    t1 = time.time()
    N = main(
        input_file=args['input_file'],
        output_dir=args['output_dir'],
        num_jobs=args['num_jobs'],
        num_proc_per_job=args['num_proc_per_job']
    )
    t2 = time.time()
    print('...done.')
    print('Total elapsed time: {:.5f}\n'.format(t2 - t1))

    # sys.stdout.write(str(N))
    # sys.exit(0)