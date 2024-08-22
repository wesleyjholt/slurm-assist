import os

def write_some_results(results_dir, tmp_dir):
    with open(os.path.join(results_dir, 'results.txt'), 'w') as f:
        f.write('some results\n')
    
    with open(os.path.join(tmp_dir, 'tmp.txt'), 'w') as f:
        f.write('some temporary stuff\n')

    print('Files written!')