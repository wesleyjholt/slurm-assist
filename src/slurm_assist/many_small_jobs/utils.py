import yaml
import csv
import pickle
from typing import Union, Mapping
ListLike = Union[list, tuple, set, range]

def load_csv(file_path):
    with open(file_path, 'r') as f:
        return [line for line in csv.reader(f)]

def load_yaml(file_path):
    with open(file_path, 'r') as f:
        return yaml.load(f, Loader=yaml.Loader)
    
def load_pickle(file_path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)

def save_csv(obj, file_path):
    with open(file_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(obj)

def save_yaml(obj, file_path):
    with open(file_path, 'w') as f:
        yaml.dump(obj, f)

def save_pickle(obj, file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(obj, f)

def check_has_keys(d, required_keys):
    for k in required_keys:
        if k not in d:
            raise ValueError(f"Missing required field: {k}")

def parse_field(field):
    if isinstance(field, ListLike):
        field = [parse_field(f) for f in field]
        return ' '.join(field)
    else:
        return str(field)

def parse_slurm_array(slurm_array):
    job_list = []
    
    # Split the array by commas to handle separate ranges/indices
    parts = slurm_array.split(',')
    
    for part in parts:
        # Check if it's a range (contains ':')
        if ':' in part:
            start, end = map(int, part.split(':'))
            job_list.extend(range(start, end + 1))
        elif '-' in part:
            start, end = map(int, part.split('-'))
            job_list.extend(range(start, end + 1))
        else:
            # Single index
            job_list.append(int(part))
    
    return job_list

# def merge_dicts(*dicts):
#     if len(dicts)==1:
#         return dicts[0]
#     merged = dicts[0]
#     for d in dicts[1:]:
#         merged.update(d)
#     return merged

# Recursive function to merge two dictionaries
def merge_dicts(*dicts):
    def _merge(dict1, dict2):
        for key, value in dict2.items():
            if isinstance(value, Mapping) and key in dict1:
                dict1[key] = _merge(dict1.get(key, {}), value)
            else:
                dict1[key] = value
        return dict1
    
    # Start with an empty dictionary
    result = {}
    
    # Merge each dictionary into the result
    for d in dicts:
        if d is not None:
            result = _merge(result, d)
    
    return result

def get_value_from_nested_dict(nested_dict, key_list):
    value = nested_dict
    for key in key_list:
        value = value[key]
    return value

# def submit_slurm_job(job_script: str, slurm_args: dict, job_script_args: Optional[list] = None, verbose=True) -> int:
#     """Submit a SLURM job using sbatch."""
#     # Convert args to a string
#     slurm_args = ' '.join([f'--{k} {parse_field(v)}' for k, v in slurm_args.items()])
#     if job_script_args is not None:
#         job_script_args = ' '.join([parse_field(arg) for arg in job_script_args])
#     else:
#         job_script_args = ''
    
#     # Submit the job
#     output = subprocess.run(["sbatch", slurm_args, job_script, job_script_args], capture_output=True, text=True)

#     if verbose:
#         print(output.args, '\n\n')
#         print(output.stdout, end='\n\n\n')

#     # Get the job ID
#     job_id = int(output.stdout.split()[-1])

#     return job_id

def estimate_total_time(num_runs, single_run_time, job_array_size, n_tasks_per_job, safety_factor=1.0):
    """Estimates the amount of time a job will take.
    
    Parameters
    ----------
    num_runs : int
        Number of independent runs.
    single_run_time : float
        Time (in seconds) for a single run.
    job_array_size : int
        Size of the job array
    n_tasks_per_job : int
        Number of tasks per job.
    safety_factor : float
    """
    total_time = num_runs*single_run_time/(job_array_size*n_tasks_per_job)*safety_factor
    hours = total_time//3600
    minutes = (total_time - hours*3600)//60
    seconds = total_time - hours*3600 - minutes*60
    print(f'{hours:.0f} hours, {minutes:.0f} minutes, {seconds:.0f} seconds')