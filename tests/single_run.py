import os

def save_txt(obj, file_path):
    with open(file_path, 'w') as f:
        f.write(obj)

def single_run(
    id: int,
    data: list[str],
    results_dir: str
) -> list[str]:
    message = f"Hello, world! I am from run id {id}, my data is {data}."
    results_file = os.path.join(results_dir, f'results_{id}.txt')
    save_txt(message, results_file)
    return data