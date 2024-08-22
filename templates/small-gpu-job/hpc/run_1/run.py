if __name__ == '__main__':
    #=============================
    # DO NOT MODIFY THIS BLOCK
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', type=str)
    parser.add_argument('--tmp', type=str)
    args = parser.parse_args()
    #=============================

    # Note: Everything in args.results directory will be moved back to the local machine.
    #       Everything in args.tmp directory will be deleted upon completion.
    
    # ADD YOUR CODE HERE!
    import sys; sys.path.append('..')    
    from example_module import hello_world, do_jax_stuff, write_some_results
    hello_world()
    do_jax_stuff()
    write_some_results(args.results, args.tmp)