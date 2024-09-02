import os
from copy import deepcopy
import subprocess
from typing import Union
import tempfile
from jinja2 import Template
from . import run, merge
from .utils import (
    load_yaml, 
    check_has_keys, 
    merge_dicts, 
    parse_field,
    parse_slurm_array, 
    estimate_total_time, 
    submit_slurm_job, 
    remove_and_make_dir, 
    cancel_slurm_job
)
from .split_data import main as split_data

parent_dir = os.path.dirname(os.path.abspath(run.__file__))
main_python_script = os.path.abspath(run.__file__)
merge_python_script = os.path.abspath(merge.__file__)

main_script_template_content = \
"""#!/bin/bash -l

module purge

# Set up tracking
module load utilities monitor
monitor cpu percent >cpu-percent-run.log &
CPU_PID=$!

# Run computations
srun --mpi={{ mpi }} apptainer run {{ container_image }} {{ python_script }} --array-id $SLURM_ARRAY_TASK_ID {{ python_script_args }}

# Shut down the resource monitors
kill -s INT $CPU_PID
"""
main_script_template = Template(main_script_template_content)

merge_script_template_content = \
"""#!/bin/bash -l

module purge

# Set up tracking
module load utilities monitor
monitor cpu percent >cpu-percent-merge.log &
CPU_PID=$!

# Run computations
apptainer run {{ container_image }} {{ python_script }} {{ python_script_args }}

# Shut down the resource monitors
kill -s INT $CPU_PID
"""
merge_script_template = Template(merge_script_template_content)

class ManySmallJobs(dict):
    def __init__(
        self, 
        *config: Union[str, dict, list[Union[str, dict, None]]]
    ):
        if isinstance(config, str):
            # Single file
            _config = load_yaml(config)
        elif isinstance(config, dict):
            # Single dictionary
            _config = config
        else:
            # List of files, dictionaries, or None values
            _configs = []
            for c in config:
                if isinstance(c, str):
                    _configs.append(load_yaml(c))
                elif isinstance(c, dict):
                    _configs.append(c)
                elif c is not None:
                    raise ValueError(f"Invalid config: {c}")
            if len(_configs) == 0:
                raise ValueError("No valid configs found.")
            _config = merge_dicts(*_configs)
        super().__init__(_config)
        self._set_defaults()
        self.check_config_is_valid()

        # The "main job"
        main_python_script_args = [
            f"--single-run-module-parent-dir {self['single_run_module_parent_dir']}",
            f"--single-run-module {self['single_run_module']}",
            f"--single-run-fn {self['single_run_fn']}",
            f"--batched-data-dir {self.batched_data_dir}",
            f"--batched-results-dir {self.batched_results_dir}",
            f"--split-results-dir {self.split_results_dir}",
            f"--job-array {self['main_slurm_args']['array']}",
            f"--parent-dir {parent_dir}"
        ]
        main_python_script_args = ' '.join([parse_field(arg) for arg in main_python_script_args])
        self.main_job_script = main_script_template.render(dict(
            container_image=self['container_image'],
            python_script=main_python_script,
            python_script_args=main_python_script_args,
            mpi=self['mpi']
        ))
        self.main_job_id = None

        # The "merge job"
        merge_python_script_args = [
            f"--batched-results-dir {self.batched_results_dir}",
            f"--merged-results-file {self.merged_results_file}",
            f"--tmp-dir {self.tmp_dir}",
            f"--job-array {self['main_slurm_args']['array']}",
            f"--ntasks-per-job {self['main_slurm_args']['ntasks']}",
            f"--parent-dir {parent_dir}"
        ]
        merge_python_script_args = ' '.join([parse_field(arg) for arg in merge_python_script_args])
        self.merge_job_script = merge_script_template.render(dict(
            container_image=self['container_image'],
            python_script=merge_python_script,
            python_script_args=merge_python_script_args,
        ))
        self.merge_job_id = None

    def check_config_is_valid(self):
        check_has_keys(self, required_keys=['main_slurm_args', 'merge_slurm_args', 'results_dir', 'input_data_file', 'container_image', 'mpi'])
        if os.path.exists(self['container_image']):
            res = subprocess.run(['apptainer', 'exec', self['container_image'], 'python3.11', '-c', 'import os'])
            if res.returncode != 0:
                raise ValueError(f"Container image '{self['container_image']}' is not valid.")
        else:
            raise ValueError(f"Container image '{self['container_image']}' does not exist.")
        if not os.path.isfile(self['input_data_file']):
            raise ValueError(f"Input data file '{self['input_data_file']}' is not a file.")
    
    def _set_defaults(self):
        if 'job-name' not in self['main_slurm_args']:
            self['main_slurm_args']['job-name'] = 'main'
        if 'job-name' not in self['merge_slurm_args']:
            self['merge_slurm_args']['job-name'] = 'merge'

    @property
    def array_elements(self):
        return parse_slurm_array(self['main_slurm_args']['array'])

    @property
    def array_size(self):
        return len(self.array_elements)
    
    @property
    def tmp_dir(self):
        if 'tmp_dir' in self.keys():
            return self['tmp_dir']
        else:
            return os.path.join(self['results_dir'], 'tmp')
    
    @property
    def job_scripts_dir(self):
        return os.path.join(self.tmp_dir, 'job_scripts')

    @property
    def batched_data_dir(self):
        return os.path.join(self.tmp_dir, 'data_batched')

    @property
    def batched_results_dir(self):
        return os.path.join(self.tmp_dir, 'results_batched')
    
    @property
    def split_results_dir(self):
        return os.path.join(self['results_dir'], 'split_results')
    
    @property
    def merged_results_file(self):
        return os.path.join(self['results_dir'], 'merged_results.txt')
    
    def _write_job_script(self, job_script_str):
        with tempfile.NamedTemporaryFile(mode='w', dir=self.job_scripts_dir, delete=False, prefix='submit_') as f:
            f.write(job_script_str)
        return f.name
    
    def setup(self):
        # Main results directory
        remove_and_make_dir(self['results_dir'])
        remove_and_make_dir(self.tmp_dir)
        os.makedirs(self.job_scripts_dir, exist_ok=True)
        os.makedirs(self.batched_data_dir, exist_ok=True)
        os.makedirs(self.batched_results_dir, exist_ok=True)
        os.makedirs(self.split_results_dir, exist_ok=True)
        
        # Split data
        split_data(
            input_file=self['input_data_file'],
            batched_data_dir=self.batched_data_dir,
            job_array=self.array_elements,
            ntasks_per_job=self['main_slurm_args']['ntasks']
        )

    def submit_main(self):
        self.setup()
        job_script_filename = self._write_job_script(self.main_job_script)
        self.main_job_id = submit_slurm_job(slurm_args=self['main_slurm_args'], job_script_filename=job_script_filename)
    
    def submit_merge(self, dependency_id=None):
        if dependency_id is not None:
            slurm_args = dict(**self['merge_slurm_args'], dependency=f"afterok:{dependency_id}")
        else:
            slurm_args = self['merge_slurm_args']
        job_script_filename = self._write_job_script(self.merge_job_script)
        self.merge_job_id = submit_slurm_job(slurm_args=slurm_args, job_script_filename=job_script_filename)
    
    def submit(self):
        self.submit_main()
        self.submit_merge(dependency_id=self.main_job_id)
    
    def cancel(self):
        cancel_slurm_job(self.main_job_id)
        cancel_slurm_job(self.merge_job_id)
        subprocess.run(["rm", "-rf", self.tmp_dir])

    def estimate_total_time(self, num_runs, single_run_time):
        """Estimate total time for all jobs to complete (not including slurm queue wait times).

        Example
        -------

        estimate_total_time(
            1000000,  # total number of runs
            180  # time per run (in seconds)
        )
        """
        estimate_total_time(
            num_runs=num_runs,
            single_run_time=single_run_time,
            job_array_size=self.array_size,
            n_tasks_per_job=self['main_slurm_args']['ntasks']
        )