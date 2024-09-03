import os
from typing import Union
from jinja2 import Template
import subprocess
from ..job import JobGroup
from ..utils import check_has_keys, remove_and_make_dir, submit_slurm_job, cancel_slurm_job, write_temp_file

script_template_content = \
"""#!/bin/bash -l

#SBATCH --output={{ stdout_dir }}/slurm-%j.out

module purge

# Set up CPU monitoring
module load utilities monitor
monitor cpu percent > {{ resource_monitoring_dir }}/cpu-percent-run-$SLURM_JOB_ID{% if is_array_job %}_$SLURM_ARRAY_TASK_ID{% endif %}.log &
CPU_USAGE_PID=$!
monitor cpu memory > {{ resource_monitoring_dir }}/cpu-memory-run-$SLURM_JOB_ID{% if is_array_job %}_$SLURM_ARRAY_TASK_ID{% endif %}.log &
CPU_MEM_PID=$!

# Set up GPU monitoring if requested
{% if use_gpu %}
module load utilities monitor
monitor gpu percent > {{ resource_monitoring_dir }}/gpu-percent-run-$SLURM_JOB_ID{% if is_array_job %}_$SLURM_ARRAY_TASK_ID{% endif %}.log &
GPU_USAGE_PID=$!
monitor gpu memory > {{ resource_monitoring_dir }}/gpu-memory-run-$SLURM_JOB_ID{% if is_array_job %}_$SLURM_ARRAY_TASK_ID{% endif %}.log &
GPU_MEM_PID=$!
{% endif %}

# Print the resource monitor directory
echo "Resource monitoring logs for this job are in {{ resource_monitoring_dir }}"

# Run computations
apptainer run {{ container_image }} {{ program }} \
{% for key, value in program_args.items() if value is not none %}\
{% if value is boolean and value %}--{{ key }} \
{% elif value is not boolean %}--{{ key }}=\"{{ value }}\" \
{% endif %}{% endfor %}

# Shut down the resource monitors
kill -s INT $CPU_USAGE_PID $CPU_MEM_PID
{% if use_gpu %}
kill -s INT $GPU_USAGE_PID $GPU_MEM_PID
{% endif %}
"""
script_template = Template(script_template_content)

class SingleJob(JobGroup):
    def __init__(
        self,
        config: Union[str, dict, list[Union[str, dict, None]]]
    ):
        super().__init__(config)
        self.check_config_is_valid()

        self.job_script = script_template.render(dict(
            container_image=self['container_image'],
            program=self['program'],
            program_args=self['program_args'],
            stdout_dir=self.stdout_dir,
            resource_monitoring_dir=self.resource_monitoring_dir
        ))
        self.job_id = None
    
    def check_config_is_valid(self):
        check_has_keys(self, required_keys=['slurm_args', 'program', 'program_args', 'results_dir', 'container_image'])
        
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
    def log_dir(self):
        if 'log_dir' in self.keys():
            return self['log_dir']
        else:
            return 'logs'
    
    @property
    def resource_monitoring_dir(self):
        return os.path.join(self.log_dir, 'resource_monitoring')
    
    @property
    def stdout_dir(self):
        return os.path.join(self.log_dir, 'stdout')
    
    def _write_job_script(self, job_script_str):
        return write_temp_file(job_script_str, dir=self.job_scripts_dir, prefix='submit_')

    def setup(self):
        remove_and_make_dir(self['results_dir'])
        remove_and_make_dir(self.tmp_dir)
        os.makedirs(self.job_scripts_dir, exist_ok=True)
        os.makedirs(self.resource_monitoring_dir, exist_ok=True)
        os.makedirs(self.stdout_dir, exist_ok=True)
    
    def submit(self, verbose=True):
        self.setup()
        job_script_filename = self._write_job_script(self.job_script)

        if verbose:
            print()
            print('SINGLE JOB')
            print('==========')

        self.job_id = submit_slurm_job(slurm_args=self['slurm_args'], job_script_filename=job_script_filename)

        if verbose:
            result = subprocess.run(
                f"scontrol show job {self.job_id} | grep -oP 'StdOut=\\K\\S+'",
                capture_output=True,
                text=True,
                shell=True
            )
            stdout_file = result.stdout.strip()
            print(f"Diagnostics")
            print(f"-----------")
            print(f"Standard output/error:          {stdout_file}")
            print(f"Resource monitoring directory:  {os.path.abspath(self.resource_monitoring_dir)}")
            print()

    
    def cancel(self):
        cancel_slurm_job(self.job_id)
        subprocess.run(["rm", "-rf", self.tmp_dir])