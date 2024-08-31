import pyslurm

script="""#!/bin/sh -l
# FILENAME:  simple_job_submission_file

#SBATCH -A myqueuename
#SBATCH --nodes=1 
#SBATCH --time=0:30:00
#SBATCH --job-name simple_test

# Print the hostname of the compute node on which this job is running.
/bin/hostname

srun --mpi=pmi2 apptainer run mpi.sif hello-world.py
"""

desc = pyslurm.JobSubmitDescription(
    name="simple_test",
    account="standby",
    nodes=1,
    memory_per_cpu=1024,
    script=script
)