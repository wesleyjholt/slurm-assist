# 1. Subclass Embarrassingly Parallel
# 2. Create a temp single run script
# 3. Pass script into Embarrassingly Parallel

import os
from ..embarrassingly_parallel.top_level_interface import EmbarrassinglyParallelJobs

class MoveFilesParallel(EmbarrassinglyParallelJobs):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        base_config = dict(
            job_name="move_files",
            single_run_module_parent_dir="move_files_single_run.sh",
        )
    
    def create_single_run_script(self):
        pass
        
    @property
    def tmp_dir(self):
        if 'tmp_dir' in self.keys():
            return os.path.relpath(self['tmp_dir'])
        else:
            return os.path.join(self['results_dir'], 'tmp')