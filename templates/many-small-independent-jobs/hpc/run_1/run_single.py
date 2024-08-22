import sys
sys.path.append('..')  # CHANGE TO WHERE YOUR CUSTOM MODULES LIVE (relative to hpc directory)
from example_module import hello_world, write_some_results  # CHANGE TO YOUR MODULES

# DO NOT TOUCH THE FUNCTION NAME OR ARGUMENTS; ONLY IMPLEMENT THE FUNCTION BODY!
def run_single(id, data, results_supplemental_dir):
    # FEEL FREE TO ADD MORE DETAILS TO THIS DOCSTRING
    """Returns the result of processing `data`.
    
    Parameters
    ----------
    id : int
        The unique run ID.
    data : any
        The input data for the run.
    results_supplemental_dir : str
        A directory to store supplemental results that are too large to be 
        included as part of the final results list. A recommended pattern is to
        store e.g. images and large arrays in this directory and let `run_single` 
        return the associated filepaths.
    """
    # IMPLEMENT ME!

    hello_world()  # DELETE ME!
    write_some_results(id, results_supplemental_dir)  # DELETE ME!

    # YOUR CODE GOES HERE :)

    return data  # REPLACE ME WITH ACTUAL RETURN VALUE!
