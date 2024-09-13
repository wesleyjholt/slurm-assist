from slurm_assist import SerialJobs, SingleJob

base_config = 'test_serial/config_base.yaml'

subjobs = [
    SingleJob([base_config, 'test_serial/config_1.yaml']),
    SingleJob([base_config, 'test_serial/config_2.yaml']),
    SingleJob([base_config, 'test_serial/config_3.yaml']),
]

jobs = SerialJobs(
    job_groups=subjobs, 
    dependency_gen_fns=lambda ids: ([[ids[-1]]], ['afterok'])
)

jobs.submit()