from slurm_assist import MoveFilesParallelJobs

job = MoveFilesParallelJobs(['test_move/config_ssh.yaml', 'test_move/config_parallel.yaml'])
job.submit()