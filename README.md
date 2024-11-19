# slurm-assist

***Submitting jobs to a Slurm-based cluster made easy!***


## tl;dr
Use Python to submit Slurm jobs (even parallel\* ones) ***without ever touching the command line***.

## Overview
This package provides a ***convenient yet flexible*** interface for several types of high-performance computing (HPC) jobs. In short, each "job type" is a python class (e.g., `SingleJob`, `EmbarrassinglyParallelJobs`) which can be created and submitted to the Slurm job scheduler *from a python script*. Many of the usual tedious tasks (setting up directory structures, writing job submission scripts, etc.) are taken care of in the background. This means less time setting up, and more time ***actually running computations***.

## Is `slurm-assist` for me?

Many common HPC tasks naturally fit into `slurm-assist`'s framework. `slurm-assist` is designed for cases where:
- You just want to get some runs going ASAP
- You want a (mostly) Python interface with the HPC
- Your workflow isn't super niche
- You are okay with using containers (this is generally a good idea)

Note that although `slurm-assist` should work on any cluster using Slurm, it has only been tested on Purdue's RCAC clusters.

## Install

```bash
pip install git+https://github.com/wesleyjholt/slurm-assist
```

## Examples

### 1. Single job

Here is the main data-processing script:
```python
# Filename: program.py

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--foo', type=str)
parser.add_argument('--bar', type=float)
args = parser.parse_args()

print(args.foo)
print(args.bar)
```

Now let's create and submit a job where we run `program.py`:
```python
# First, create the necessary configurations
config = {
    'results_dir': results,
    'program': ./program.py,
    'program_args': {
        'foo': "I_am_the_argument_foo",
        'bar': 100.0
    },
    'container_image': mpi.sif,  # This is an apptainer image
    'slurm_args': {
        # These arguments are passed to the sbatch call
        'job-name': single_job,
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

### 2. Parallel, independent jobs
Define how to perform a single run:
```python
# Filename: single_run.py
import os

def save_txt(obj, file_path):
    with open(file_path, 'w') as f:
        f.write(obj)

def single_run(
    id: int,
    data: list[str],
    results_dir: str,
    extra_arg_1: str,
    extra_arg_2: str,
) -> list[str]:
    message = f"Hello, world! I am from run id {id}, my data is {data}.\n"
    message += f"Extra args: {extra_arg_1}, {extra_arg_2}"
    results_file = os.path.join(results_dir, f'results_{id}.txt')
    save_txt(message, results_file)
    return data
```

Create configuration files that contain the following fields:
```yaml
# Filename: config.yaml
input_data_file: test_embarrassingly_parallel/data.txt
single_run_module_parent_dir: ./test_embarrassingly_parallel
single_run_module: single_run
single_run_function: single_run
container_image: mpi.sif
mpi: pmi2
generate_new_ids: true
main_slurm_args: 
  array: 1-4
  time: 00:20:00
  mem-per-cpu: 1024M
  ntasks: 2
  account: standby
merge_slurm_args:
  time: 00:20:00
results_dir: test_embarrassingly_parallel/results
tmp_dir: test_embarrassingly_parallel/tmp
_main_python_script_extra_args: 
  extra_arg_1: hello
  extra-arg-2: world
```
(Alternatively, you can use a dictionary instead of a yaml file. See "single job" example above.)

Now submit the job:
```python
from slurm_assist import EmbarrassinglyParallelJobs

job = EmbarrassinglyParallelJobs('config.yaml')
job.submit()
```
(Note that we could pass in a list of dictionaries or configuration files. If multiple configuration dicts/files specify the same field, then the first configurations will take precedence over the later ones.)

### 3. Chained jobs
Create the main data-processing script:
```python
# Filename: program.py
if __name__=='__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--foo', type=str)
    parser.add_argument('--bar', type=float)
    args = parser.parse_args()

    print('foo is a variable of type: ', type(args.foo))
    print('The value of foo is: ', args.foo)
    print('bar is a variable of type: ', type(args.bar))
    print('The value of bar + 1 is: ', args.bar + 1)
```

Create the configuration files.
You can set global configurations:
```yaml
# Filename: global_config.yaml

program: ./program.py  # Required
program_args:  # Required
  foo: "I_am_the_argument_foo"
container_image: mpi.sif  # Required
slurm_args:  # Required
  time: "00:05:00"
  nodes: 1
  ntasks: 1
  mem-per-cpu: "1024M"
  array: 1-3
```
As well as job-specific configurations:
```yaml
# Filename: job_1_config.yaml

results_dir: results_1
program_args:
  bar: 100.0
slurm_args:
  job-name: test_serial_1
```

Now we can submit the chained jobs:
```python
from slurm_assist import SerialJobs, SingleJob

base_config = 'global_config.yaml'

subjobs = [
    SingleJob([base_config, 'job_1_config.yaml']),
    SingleJob([base_config, 'job_2_config.yaml']),
    SingleJob([base_config, 'job_3_config.yaml']),
]

jobs = SerialJobs(
    job_groups=subjobs, 
    dependency_gen_fns=lambda ids: ([[ids[-1]]], ['afterok'])
)

jobs.submit()
```

There is also an alternative API for chained jobs that is more flexible to allow for things like jobs whose specifications depend on the results of previous jobs.
It works by defining a "state" for the serial jobs which evolves as each job in the chain is submitted.
Here is the same example with the alternative API:
```python
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
```
See the documentation for more details.

## Containers

For now, all jobs require you to run your data processing program (e.g., the python script that does the computation) within an [apptainer](https://apptainer.org/docs/user/main/index.html) container.

## Documentation

***Coming soon!***


Note that this package is not yet operating system agnostic. 
In particular, it is designed for Mac/Linux users. 
Several functions will not work with Windows computers.
---
\* Only specific types of parallel jobs (i.e., "embarrassingly parallel") are supported.