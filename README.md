# hpc-templates

Templates for file/directory structures useful for running jobs on Purdue RCAC's remote clusters.

In particular, these templates are designed specifically for using
- Python for data processing
- Apptainer for containerization
- SLURM for job scheduling
- MPI for message passing (when applicable)

## Dependencies

You will need Python 3.5+ on your local machine to run these push/pull scripts. You will also need the [gitignore_parser](https://github.com/mherrmann/gitignore_parser/tree/master) python package:

```bash
pip install gitignore_parser
```