# Each job takes in config files and outputs results.
# Each transition takes in config files and outputs more config files.

from typing import Union, Callable, Optional, Sequence, Any
from ..job import JobGroup
from ..utils import check_has_keys

Config = Union[str, dict, list[Union[str, dict, None]]]

class SerialJobs(JobGroup):
    def __init__(
        self,
        config: Config,
        job_group_gen_fns: list[Callable[[Config], JobGroup]],
        config_gen_fns: list[Callable[[Config, Any], tuple[Config, Any]]],
        num_loops: Optional[int] = None,
        config_gen_state: Any = None
    ):
        super().__init__(config)
        self._config = super().__new__(config)
        self.i_submit = 0
        if num_loops is not None:
            all_job_group_gen_fns, all_config_gen_fns = [], []
            for _ in range(num_loops):
                all_job_group_gen_fns += [job_group_gen_fns]
                all_config_gen_fns += [config_gen_fns]
            self.job_group_gen_fns = all_job_group_gen_fns
            self.config_gen_fns = all_config_gen_fns
        else:
            self.job_group_gen_fns = job_group_gen_fns
            self.config_gen_fns = config_gen_fns
        self.config_gen_state = config_gen_state
        self.job_groups = []
    
    def submit_next(self):
        config_i, self.config_gen_state = self.config_gen_fns[self.i_submit](self._config, self.config_gen_state)
        job_group_i = self.job_group_gen_fns[self.i_submit](config_i)
        last_job_id = job_group_i.submit()  # this id should be a list
        self.i_submit += 1

    def submit(self):
        while self.i_submit < len(self.job_groups):
            self.submit_next()