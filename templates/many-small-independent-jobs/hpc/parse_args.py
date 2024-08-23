if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Parse arguments')
    parser.add_argument('--run-name', type=str, help='Name of the run in the current hpc directory', required=True)
    parser.add_argument('--project-root-dir', type=str, help='Path to the project root directory')
    parser.add_argument('--pull-supplemental', action='store_true', help='Pull supplemental results files')
    args = parser.parse_args()

    print(f'export RUN_NAME={args.run_name}', end='; ')
    if args.project_root_dir is not None:
        print(f'export PROJECT_ROOT_DIR={args.project_root_dir}', end='; ')
    if args.pull_supplemental:
        print('export PULL_SUPPLEMENTAL=1', end='; ')
    else:
        print('export PULL_SUPPLEMENTAL=0', end='; ')