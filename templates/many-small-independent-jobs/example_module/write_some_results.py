import os

def write_some_results(id, results_dir):
    with open(os.path.join(results_dir, f'results_{id}.txt'), 'w') as f:
        f.write('some results\n')

    print('Files written!')