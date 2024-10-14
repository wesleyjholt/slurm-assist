from .utils import load_yaml, merge_dicts, convert_slurm_keys, cancel_slurm_job, parse_config

class JobGroup(dict):
    def __init__(self, config):
        parsed_config = parse_config(config)
        if parsed_config is None:
            # No config
            super().__init__()
        else:
            super().__init__(parsed_config)
        self.all_job_ids = []
    
    def submit(self):
        raise NotImplementedError('submit method is not implemented. Implement me!')
    
    def cancel(self):
        for job_id in self.all_job_ids:
            cancel_slurm_job(job_id)
    
    