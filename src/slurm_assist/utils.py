import os
import csv
import pickle
import subprocess
import tempfile

from typing import Union, Mapping, Optional
ListLike = Union[list, tuple, set, range]

def load_text(file_path):
    with open(file_path, 'r') as f:
        return f.read()

def load_csv(file_path):
    with open(file_path, 'r') as f:
        return [line for line in csv.reader(f)]

def load_yaml(file_path):
    import yaml
    with open(file_path, 'r') as f:
        return yaml.load(f, Loader=yaml.Loader)
    
def load_pickle(file_path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)

def append_text(obj, file_path):
    with open(file_path, 'a') as f:
        f.write(obj)

def save_text(obj, file_path):
    with open(file_path, 'w') as f:
        f.write(obj)

def save_csv(obj, file_path):
    with open(file_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(obj)

def save_yaml(obj, file_path):
    import yaml
    with open(file_path, 'w') as f:
        yaml.dump(obj, f)

def save_pickle(obj, file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(obj, f)

def write_temp_file(
    obj: str, 
    dir: Optional[str] = None, 
    prefix: Optional[str] = None
):
    with tempfile.NamedTemporaryFile(mode='w', dir=dir, delete=False, prefix=prefix) as f:
        f.write(obj)
    return f.name

def remove_and_make_dir(dir):
    if os.path.exists(dir):
        subprocess.run(["rm", "-rf", dir])
    os.makedirs(dir, exist_ok=True)

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

def to_zero_based_indexing(ind: Union[int, list]):
    if isinstance(ind, int):
        return ind - 1
    else:
        return list(map(lambda x: x - 1), ind)

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

def cancel_slurm_job(job_id: int, verbose: bool = True):
    output = subprocess.run(['scancel', str(job_id)], capture_output=True, text=True)
    if output.stderr != '':
        print(output.stderr)
    if verbose:
        print(output.stdout)

def submit_slurm_job(
    slurm_args: dict, 
    job_script_filename: str, 
    verbose: bool = Optional[True],
    dependency_ids: Optional[list[list[int]]] = None, 
    dependency_conditions: Optional[list[str]] = None
):
    from jinja2 import Template
    submit_command_template_content = \
"""sbatch \
{% for key, value in slurm_args.items() if value is not none %}\
{% if value is boolean and value %}--{{ key }} \
{% elif value is not boolean %}--{{ key }}={{ value }} \
{% endif %}{% endfor %} \
{{ job_script_filename }}
"""
    submit_command_template = Template(submit_command_template_content)

    if (dependency_ids is not None) and (dependency_conditions is not None):
        dependencies_str = format_dependencies_to_str(dependency_ids, dependency_conditions)
        slurm_args = dict(**slurm_args, dependency=dependencies_str)
    elif (dependency_ids is None) ^ (dependency_conditions is None):
        raise RuntimeError(f'Cannot specify only one of dependency_ids ({dependency_ids}) and dependency_conditions ({dependency_conditions}).')

    env = os.environ.copy()
    sbatch_command = submit_command_template.render(slurm_args=slurm_args, job_script_filename=job_script_filename)
    output = subprocess.run(sbatch_command, capture_output=True, text=True, shell=True, env=env)
    if output.stderr != '':
        print(output.stderr)
    if verbose:
        print()
        print('Submit command')
        print('--------------')
        print(sbatch_command)
        print()
        print('Confirmation')
        print('------------')
        print(output.stdout)
    job_id = int(output.stdout.split()[-1])
    return job_id

def format_dependencies_to_str(ids: list[list[int]], conditions: list[str]) -> str:
    # Check if the lengths of the ids and conditions match
    if len(ids) != len(conditions):
        raise ValueError("The length of 'ids' and 'conditions' must be the same.")

    # Initialize an empty list to hold the parsed dependencies
    dependencies = []

    # Iterate over the conditions and corresponding job ID lists
    for job_ids, condition in zip(ids, conditions):
        # Create a dependency string for each set of job IDs
        dependency = f"{condition}:" + ":".join(map(str, job_ids))
        dependencies.append(dependency)

    # Join all dependency strings into a single string with commas
    return ",".join(dependencies)

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