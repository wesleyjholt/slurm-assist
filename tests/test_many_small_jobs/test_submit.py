import os
from slurm_assist import ManySmallJobs

job = ManySmallJobs('test_many_small_jobs/config_1.yaml', 'test_many_small_jobs/config_2.yaml')

job.submit()