from slurm_assist import SerialJobsWithState, SingleJob

base_config = 'test_serial/config_base.yaml'

jobs = SerialJobsWithState(
    state=1,  # This is just the config file counter/identifier
    config=None, 
    job_group_gen_fns=lambda config, _: (SingleJob(config), _), 
    config_gen_fns=lambda _, i: ([base_config, f'test_serial/config_{i}.yaml'], i+1), 
    dependency_gen_fns=lambda ids, _: (([[ids[-1]]], ['afterok']), _),
    num_loops=3
)

jobs.submit()