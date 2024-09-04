from slurm_assist import SerialJobs, SingleJob

base_config = 'test_serial/config_base.yaml'

jobs = SerialJobs(
    config=None, 
    job_group_gen_fns=lambda config, _: (SingleJob(config), _), 
    config_gen_fns=lambda _, i: ([base_config, f'test_serial/config_{i}.yaml'], i+1), 
    dependency_gen_fns=lambda ids, _: (([[ids[-1]]], ['afterok']), _),
    num_loops=3,
    state=1  # This is just the config file counter/identifier
)

jobs.submit()