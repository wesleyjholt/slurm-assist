from slurm_assist import EmbarrassinglyParallelJobs

job = EmbarrassinglyParallelJobs(['test_embarrassingly_parallel/config_1a.yaml', 'test_embarrassingly_parallel/config_2.yaml'])
job.submit()