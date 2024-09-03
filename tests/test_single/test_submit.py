from slurm_assist import SingleJob

job = SingleJob(['test_single/config.yaml', None])
job.submit()