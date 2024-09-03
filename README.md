# slurm-assist

***Submitting jobs to a Slurm-based cluster made easy!***


## tl;dr
You can submit Slurm jobs (yes, even parallel\* ones) all from a python notebook ***without ever touching the command line***.

## Overview
This package provides a ***convenient yet flexible*** interface for several types of high-performance computing (HPC) jobs. In short, each "job type" is a python class (e.g., `SingleJob`, `EmbarrassinglyParallelJobs`) which can be created and submitted to the Slurm job scheduler *from a python script*. Many of the usual tedious tasks (setting up directory structures, writing job submission scripts, etc.) are taken care of in the background. This means less time setting up, and more time ***actually running computations***.

## Is `slurm-assist` for me?

Many common HPC tasks naturally fit into `slurm-assist`'s framework. `slurm-assist` is designed for cases where:
- You just want to get some runs going ASAP
- You want a (mostly) pure python interface with the HPC
- Your workflow isn't super niche
- You are okay with using containers (this is generally a good idea)

Note that although `slurm-assist` should work on any cluster using Slurm, it has only been tested on Purdue's RCAC clusters.

## Install

```bash
pip install git+https://github.com/wesleyjholt/slurm-assist
```

## Examples

### Single job
```python
# First, create the necessary configurations
config = {
    'input_data_file': test_single/data.txt,
    'results_dir': test_single/results,
    'program': ./test_single/program.py,
    'program_args': {
        'foo': "I_am_the_argument_foo",
        'bar': 100.0
    },
    'container_image': mpi.sif,  # This is an apptainer image
    'slurm_args': {
        # These arguments are passed to the sbatch call
        'job-name': test_single,
        'time': "00:05:00",
        'nodes': 1,
        'ntasks': 1,
        'mem-per-cpu': "1024M"
    }
}

# Next, create a job object
from slurm_assist import SingleJob
job = SingleJob(config)

# And, finally, submit the job
job.submit()
```

### Parallel, independent jobs
TODO: Add example here

### Chained jobs
TODO: Add example here

## Containers

For now, all jobs require you to run your data processing program (e.g., the python script that does the computation) within an [apptainer](https://apptainer.org/docs/user/main/index.html) container.

## Documentation

***Coming soon!***

---
\* Only specific types of parallel jobs (i.e., "embarrassingly parallel") are supported.