from slurm_assist import SerialJobs, SingleJob

base_config = 'test_serial/config_base.yaml'

# job1 = SingleJob([base_config, 'test_serial/config_1.yaml'])
# job2 = SingleJob([base_config, 'test_serial/config_2.yaml'])
# job3 = SingleJob([base_config, 'test_serial/config_3.yaml'])

jobs = SerialJobs(
    config=None, 
    job_group_gen_fns=SingleJob, 
    config_gen_fns=lambda _, i: ([base_config, 'test_serial/config_{i}.yaml'], i+1), 
    num_loops=3,
    config_gen_state=1
)

jobs.submit()