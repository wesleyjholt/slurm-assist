import os
from typing import Union
from jinja2 import Template
import subprocess
from ..job import JobGroup
from ..utils import check_has_keys, remove_and_make_dir, submit_slurm_job, cancel_slurm_job, write_temp_file

script_template_content = \
"""#!/bin/bash -l

module purge

# Set up tracking
module load utilities monitor
monitor cpu percent > cpu-percent-run-$SLURM_JOB_ID.log &
CPU_PID=$!
monitor cpu memory > cpu-memory-run-$SLURM_JOB_ID.log &
MEM_PID=$!
monitor gpu percent > gpu-percent-run-$SLURM_JOB_ID.log &
GPU_PID=$!

# Run computations
apptainer run {{ container_image }} {{ program }} \
{% for key, value in program_args.items() if value is not none %}\
{% if value is boolean and value %}--{{ key }} \
{% elif value is not boolean %}--{{ key }}={{ value }} \
{% endif %}{% endfor %}

# Shut down the resource monitors
kill -s INT $CPU_PID $MEM_PID $GPU_PID
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
            program_args=self['program_args']
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
    
    def _write_job_script(self, job_script_str):
        return write_temp_file(job_script_str, dir=self.job_scripts_dir, prefix='submit_')

    def setup(self):
        remove_and_make_dir(self['results_dir'])
        remove_and_make_dir(self.tmp_dir)
        os.makedirs(self.job_scripts_dir, exist_ok=True)
    
    def submit(self):
        self.setup()
        job_script_filename = self._write_job_script(self.job_script)
        self.job_id = submit_slurm_job(slurm_args=self['slurm_args'], job_script_filename=job_script_filename)
    
    def cancel(self):
        cancel_slurm_job(self.job_id)
        subprocess.run(["rm", "-rf", self.tmp_dir])