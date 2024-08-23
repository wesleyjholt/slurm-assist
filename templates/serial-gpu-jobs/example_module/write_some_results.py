import os

def write_some_results(results_dir, tmp_dir):
    results_file = os.path.join(results_dir, 'results.txt')

    if not os.path.exists(results_file):
        with open(results_file, 'w') as f:
            f.write('')

    with open(results_file, 'a') as f:
        f.write('some results\n')
    
    with open(os.path.join(tmp_dir, 'tmp.txt'), 'w') as f:
        f.write('some temporary stuff\n')

    print('Files written!')