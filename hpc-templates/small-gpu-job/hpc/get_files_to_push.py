from gitignore_parser import parse_gitignore
import os
from glob import glob

def get_relevant_files(hpc_dir, project_root_dir, run_name, ignore_patterns=[]):
    """Obtains relevant files to push to the HPC cluster.
    
    This function returns... 
        all files in project_root_dir...
        except files in run folders other than run_name...
        and except files ignored by .hpc-ignore.
    """
    def get_only_files(files):
        return [file for file in files if os.path.isfile(file)]
    
    project_root_dir_relpath = os.path.relpath(project_root_dir, hpc_dir)
    hpc_dir_relpath = os.path.relpath(hpc_dir, project_root_dir)
        
    # Get all files in the project directory
    files = glob(os.path.join(project_root_dir_relpath, '**'), recursive=True)

    # Get only files
    files = get_only_files(files)

    # Apply .hpc-ignore patterns
    ignore_file = os.path.join(project_root_dir_relpath, '.hpc-ignore')
    if os.path.exists(ignore_file):
        ignore = parse_gitignore(ignore_file)
        files = [file for file in files if not ignore(file)]

    # Remove files that match ignore_patterns
    if len(ignore_patterns) > 0:
        ignore_tmp_file = os.path.join(project_root_dir_relpath, '.hpc-ignore-tmp')
        with open(ignore_tmp_file, 'w') as f:
            for pattern in ignore_patterns:
                f.write(pattern+'\n')
        ignore = parse_gitignore(ignore_tmp_file)
        files = [file for file in files if not ignore(file)]
        os.remove(ignore_tmp_file)

    # Exclude files in irrelevant run folders
    files_in_all_run_folders = get_only_files(glob(os.path.join(project_root_dir_relpath, hpc_dir_relpath, '*', '**'), recursive=True))
    files_in_relevant_run_folders = get_only_files(glob(os.path.join(project_root_dir_relpath, hpc_dir_relpath, run_name, '**'), recursive=True))
    files_in_irrelevant_run_folders = [file for file in files_in_all_run_folders if file not in files_in_relevant_run_folders]
    files = [file for file in files if file not in files_in_irrelevant_run_folders]
    
    return files

if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--hpc-dir", default='./')
    parser.add_argument("--project-root-dir", required=True)
    parser.add_argument("--run-name", required=True)
    parser.add_argument("--ignore-patterns", nargs='*')
    args = parser.parse_args()

    files = get_relevant_files(args.hpc_dir, args.project_root_dir, args.run_name, args.ignore_patterns)
    for file in files:
        print(file)