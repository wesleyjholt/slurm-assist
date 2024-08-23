if __name__ == '__main__':
    #=============================
    # Do not modify this block!
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', type=str)
    parser.add_argument('--tmp', type=str)

    # Note: Everything in args.results directory will be moved back to the local machine.
    #       Everything in args.tmp directory will be deleted upon job completion.

    # Note: This script will receive as input a line from the file 'run_args'.
    #       Which line will depend on the job's position in the sequence.
    #=============================


    # ADD ADDITIONAL ARGUMENTS HERE!
    # parser.add_argument(...)


    #=============================
    # Do not modify this block!
    args, _ = parser.parse_known_args()
    #=============================
    
    # REPLACE BELOW WITH YOUR OWN CODE!
    import sys; sys.path.append('..')
    from example_module import hello_world, do_jax_stuff, write_some_results
    hello_world()
    do_jax_stuff()
    write_some_results(args.results, args.tmp)