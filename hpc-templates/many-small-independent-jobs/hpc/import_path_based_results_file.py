import os
import pickle

def open_pkl(path):
    with open(path, 'rb') as f:
        return pickle.load(f)

def save_pkl(obj, path):
    with open(path, 'wb') as f:
        pickle.dump(obj, f)

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Import path-based results file')
    parser.add_argument('--run-name', type=str, help='Name of the run in the current hpc directory')
    parser.add_argument('--other-hpc-dir', type=str, help='Path to the other hpc directory')
    parser.add_argument('--other-run-name', type=str, help='Name of the run in the other hpc directory')
    parser.add_argument('--check-paths', action='store_true', help='Check that all paths in the results file exist')
    args = parser.parse_args()

    # Get contents of the results file
    other_results_file = os.path.join(args.other_hpc_dir, args.other_run_name, 'results/results.pkl')
    other_results = open_pkl(other_results_file)

    # Check that the results file is valid
    if not isinstance(other_results, list):
        raise ValueError(f'Invalid results file: {other_results_file}. The contents must be a list.')
    if not all([isinstance(x, str) for x in other_results]):
        raise ValueError(f'Invalid results file: {other_results_file}. Each element of the list must be a string.')
    if args.check_paths:
        if not all([os.path.exists(os.path.join(args.other_hpc_dir, x)) for x in other_results]):
            raise ValueError(f'Invalid path: {other_results_file[0]}. One or more paths do not exist.')
    
    # Create and save a new results file
    new_paths = [os.path.relpath(os.path.join(args.other_hpc_dir, x), './') for x in other_results]
    results_dir = os.path.join(args.run_name, 'results')
    os.makedirs(results_dir, exist_ok=True)
    save_pkl(new_paths, os.path.join(results_dir, 'results.pkl'))