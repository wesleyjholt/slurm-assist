This template is for performing many jobs which all do the same thing and run independently from one another. 

## Tutorial

See `tutorial.ipynb`.

## Files
`split_data.py` takes a list of input data and splits it into batches to be proceesed in parallel.

`run.py` does the data processing.

`merge_data.py` takes the output from each batch and merges it into a single list.