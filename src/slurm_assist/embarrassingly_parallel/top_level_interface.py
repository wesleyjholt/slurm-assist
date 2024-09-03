import os
import subprocess
from typing import Union, Optional
from collections import namedtuple
import tempfile
from jinja2 import Template
from . import run, merge
from ..job import JobGroup
from ..utils import (
    check_has_keys, 
    parse_field,
    parse_slurm_array, 
    estimate_total_time, 
    submit_slurm_job, 
    remove_and_make_dir, 
    cancel_slurm_job,
    write_temp_file
)
from .split_data import main as split_data

from .. import utils
utils_parent_dir = os.path.dirname(os.path.abspath(utils.__file__))
main_python_script = os.path.abspath(run.__file__)
merge_python_script = os.path.abspath(merge.__file__)

main_script_template_content = \
"""#!/bin/bash -l

#SBATCH --output={{ stdout_dir }}/slurm-%A_%a.out

module purge

# Set up CPU monitoring
module load utilities monitor
monitor cpu percent > {{ resource_monitoring_dir }}/cpu-percent-run-${SLURM_JOB_ID}_${SLURM_ARRAY_TASK_ID}.log &
CPU_USAGE_PID=$!
monitor cpu memory > {{ resource_monitoring_dir }}/cpu-memory-run-${SLURM_JOB_ID}_${SLURM_ARRAY_TASK_ID}.log &
CPU_MEM_PID=$!

# Set up GPU monitoring if requested
{% if use_gpu %}
module load utilities monitor
monitor gpu percent > {{ resource_monitoring_dir }}/gpu-percent-run-${SLURM_JOB_ID}_${SLURM_ARRAY_TASK_ID}.log &
GPU_USAGE_PID=$!
monitor gpu memory > {{ resource_monitoring_dir }}/gpu-memory-run-${SLURM_JOB_ID}_${SLURM_ARRAY_TASK_ID}.log &
GPU_MEM_PID=$!
{% endif %}

# Run computations
srun --mpi={{ mpi }} apptainer run {{ container_image }} {{ python_script }} --array-id $SLURM_ARRAY_TASK_ID {{ python_script_args }}

# Shut down the resource monitors
kill -s INT $CPU_USAGE_PID $CPU_MEM_PID
{% if use_gpu %}
kill -s INT $GPU_USAGE_PID $GPU_MEM_PID
{% endif %}
"""
main_script_template = Template(main_script_template_content)

merge_script_template_content = \
"""#!/bin/bash -l

#SBATCH --output={{ stdout_dir }}/slurm-%j.out

module purge

# Set up CPU monitoring
module load utilities monitor
monitor cpu percent > {{ resource_monitoring_dir }}/cpu-percent-run-${SLURM_JOB_ID}.log &
CPU_USAGE_PID=$!
monitor cpu memory > {{ resource_monitoring_dir }}/cpu-memory-run-${SLURM_JOB_ID}.log &
CPU_MEM_PID=$!

# Run computations
apptainer run {{ container_image }} {{ python_script }} {{ python_script_args }}

# Shut down the resource monitors
kill -s INT $CPU_USAGE_PID $CPU_MEM_PID
"""
merge_script_template = Template(merge_script_template_content)

class EmbarrassinglyParallelJobs(JobGroup):
    def __init__(
        self, 
        config: Union[str, dict, list[Union[str, dict, None]]]
    ):
        super().__init__(config)
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
            f"--utils-parent-dir {utils_parent_dir}"
        ]
        main_python_script_args = ' '.join([parse_field(arg) for arg in main_python_script_args])
        self.main_job_script = main_script_template.render(dict(
            container_image=self['container_image'],
            python_script=main_python_script,
            python_script_args=main_python_script_args,
            mpi=self['mpi'],
            use_gpu=self['use_gpu'],
            stdout_dir=self.stdout_dir,
            resource_monitoring_dir=self.resource_monitoring_dir
        ))
        self.main_job_id = None

        # The "merge job"
        merge_python_script_args = [
            f"--batched-results-dir {self.batched_results_dir}",
            f"--merged-results-file {self.merged_results_file}",
            f"--tmp-dir {self.tmp_dir}",
            f"--job-array {self['main_slurm_args']['array']}",
            f"--ntasks-per-job {self['main_slurm_args']['ntasks']}",
            f"--utils-parent-dir {utils_parent_dir}"
        ]
        merge_python_script_args = ' '.join([parse_field(arg) for arg in merge_python_script_args])
        self.merge_job_script = merge_script_template.render(dict(
            container_image=self['container_image'],
            python_script=merge_python_script,
            python_script_args=merge_python_script_args,
            stdout_dir=self.stdout_dir,
            resource_monitoring_dir=self.resource_monitoring_dir
        ))
        self.merge_job_id = None

    def check_config_is_valid(self, container_test_cmds=['python3', '-c', 'import os']):
        check_has_keys(self, required_keys=['main_slurm_args', 'merge_slurm_args', 'results_dir', 'input_data_file', 'container_image', 'mpi'])
        if os.path.exists(self['container_image']):
            res = subprocess.run(['apptainer', 'exec', self['container_image'], *container_test_cmds])
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
        if 'use_gpu' not in self:
            self['use_gpu'] = False

    @property
    def array_elements(self):
        return parse_slurm_array(self['main_slurm_args']['array'])

    @property
    def array_size(self):
        return len(self.array_elements)
    
    @property
    def tmp_dir(self):
        if 'tmp_dir' in self.keys():
            return os.path.relpath(self['tmp_dir'])
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
    def log_dir(self):
        if 'log_dir' in self.keys():
            return os.path.relpath(self['log_dir'])
        else:
            return 'logs'
    
    @property
    def resource_monitoring_dir(self):
        return os.path.join(self.log_dir, 'resource_monitoring')
    
    @property
    def stdout_dir(self):
        return os.path.join(self.log_dir, 'stdout')
    
    @property
    def split_results_dir(self):
        return os.path.join(self['results_dir'], 'split_results')
    
    @property
    def merged_results_file(self):
        return os.path.join(self['results_dir'], 'merged_results.txt')
    
    def _write_job_script(self, job_script_str):
        return write_temp_file(job_script_str, dir=self.job_scripts_dir, prefix='submit_')
    
    def setup(self):
        # Main results directory
        remove_and_make_dir(self['results_dir'])
        remove_and_make_dir(self.tmp_dir)
        os.makedirs(self.job_scripts_dir, exist_ok=True)
        os.makedirs(self.batched_data_dir, exist_ok=True)
        os.makedirs(self.batched_results_dir, exist_ok=True)
        os.makedirs(self.split_results_dir, exist_ok=True)
        os.makedirs(self.resource_monitoring_dir, exist_ok=True)
        os.makedirs(self.stdout_dir, exist_ok=True)
        
        # Split data
        split_data(
            input_file=self['input_data_file'],
            batched_data_dir=self.batched_data_dir,
            job_array=self.array_elements,
            ntasks_per_job=self['main_slurm_args']['ntasks']
        )

    def submit_main(self, **kwargs):
        self.setup()
        job_script_filename = self._write_job_script(self.main_job_script)
        self.main_job_id = submit_slurm_job(
            slurm_args=self['main_slurm_args'], 
            job_script_filename=job_script_filename, 
            **kwargs
        )
    
    def submit_merge(self, **kwargs):
        job_script_filename = self._write_job_script(self.merge_job_script)
        self.merge_job_id = submit_slurm_job(
            slurm_args=self['merge_slurm_args'], 
            job_script_filename=job_script_filename, 
            dependency_ids=[[self.main_job_id]], 
            dependency_conditions=['afterok'],
            **kwargs
        )
    
    def submit(
        self, 
        dependency_ids: Optional[list[list[int]]] = None, 
        dependency_conditions: Optional[list[str]] = None,
        verbose: Optional[bool] = True
    ) -> tuple[int]:
        """Submits the jobs. Returns ID of the last job(s) in the dependency chain."""
        if verbose:
            print()
            print('MAIN JOB')
            print('========')

        self.submit_main(dependency_ids=dependency_ids, dependency_conditions=dependency_conditions)

        if verbose:
            print(f"Diagnostics")
            print(f"-----------")
            print(f"Standard output/error files:    {os.path.abspath(self.stdout_dir)}/slurm-{self.main_job_id}_*.out")
            print(f"Resource monitoring directory:  {os.path.abspath(self.resource_monitoring_dir)}")
            print()

        if verbose:
            print()
            print('MERGE JOB')
            print('=========')

        self.submit_merge()

        if verbose:
            print(f"Diagnostics")
            print(f"-----------")
            print(f"Standard output/error files:    {os.path.abspath(self.stdout_dir)}/slurm-{self.merge_job_id}.out")
            print(f"Resource monitoring directory:  {os.path.abspath(self.resource_monitoring_dir)}")
            print()

        JobIds = namedtuple('JobIds', ['main', 'merge'])
        return JobIds(main=self.main_job_id, merge=self.merge_job_id)
    
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