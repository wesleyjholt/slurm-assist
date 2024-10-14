# 1. Subclass Embarrassingly Parallel
# 2. Create a temp single run script
# 3. Pass script into Embarrassingly Parallel

import os
from jinja2 import Template
import tempfile
from ..utils import write_temp_file, check_has_keys, parse_config
from ..embarrassingly_parallel.top_level_interface import EmbarrassinglyParallelJobs

single_run_python_script = \
"""
from slurm_assist.utils import compress_and_transfer

def single_run(
    id: int,
    data: list[str],
    results_dir: str,
):
    # Get the files to move
    local_path = data[0]
    
    # Compress and transfer the files to the remote server
    remote_paths = compress_and_transfer(
        {{ hostname }}, 
        {{ username }}, 
        {{ key_filename }}, 
        [local_path], 
        {{ remote_dir }}
    )
    remote_path = remote_paths[0]
"""
single_run_python_script_template = Template(single_run_python_script)

class MoveFilesParallelJobs(EmbarrassinglyParallelJobs):
    def __init__(self, config):
        config = parse_config(config)
        check_has_keys(config, required_keys=['hostname', 'username', 'key_filename', 'remote_dir', 'results_dir'])
        self.single_run_python_script = single_run_python_script_template.render(dict(
            hostname=config['hostname'],
            username=config['username'],
            key_filename=config['key_filename'],
            remote_dir=config['remote_dir']
        ))

        single_run_path = os.path.abspath(self._write_single_run_python_script(config))

        base_config = dict(
            job_name="move_files",
            single_run_module_parent_dir=os.path.relpath(os.path.dirname(single_run_path)),
            single_run_module=os.path.basename(single_run_path),
            single_run_function='single_run'
        )
        # TODO: Figure out why it is not finding the single_run_module. Print the base_config to make sure it is correct.
        if isinstance(config, str | dict):
            config = [config]
        super().__init__(config + [base_config])
    
    # def submit(self):
    #     # self._write_single_run_python_script()
    #     super().submit()

    def _write_single_run_python_script(self, config):
        tmp_dir = config['tmp'] if 'tmp' in config else 'tmp_move'
        os.makedirs(tmp_dir, exist_ok=True)
        return write_temp_file(self.single_run_python_script, dir=tmp_dir, prefix='move_files_')
        # return self._write_job_script(self.single_run_python_script, dir=self.job_scripts_dir, prefix='move_files_')
        
    # @property
    # def tmp_dir(self):
    #     if 'tmp_dir' in self.keys():
    #         return os.path.relpath(self['tmp_dir'])
    #     else:
    #         return os.path.join(self['results_dir'], 'tmp')

    # def _write_single_run_script(self):
    #     return write_temp_file(job_script_str, dir=self.job_scripts_dir, prefix='ssh_move_')