import os

def get_file_sizes(dir_names):
    """
    Get the sizes of all files in the given directories.

    :param dir_names: List of directory paths
    :return: A list of tuples where each tuple is (file_path, file_size)
    """
    file_sizes = []
    for dir_name in dir_names:
        for root, _, files in os.walk(dir_name):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    file_sizes.append((file_path, size))
                except OSError:
                    print(f"Could not access file {file_path}")
    return file_sizes

def distribute_files(file_sizes, n):
    """
    Distribute files into N groups with roughly equal total sizes.

    :param file_sizes: List of tuples (file_path, file_size)
    :param n: Number of groups
    :return: A list of lists where each sublist contains file paths
    """
    # Sort files by size in descending order
    file_sizes.sort(key=lambda x: x[1], reverse=True)

    # Initialize N empty lists for the groups
    groups = [[] for _ in range(n)]
    group_sizes = [0] * n  # Track the total size of each group

    for file_path, size in file_sizes:
        # Find the group with the smallest total size and add the file there
        smallest_group_index = group_sizes.index(min(group_sizes))
        groups[smallest_group_index].append(file_path)
        group_sizes[smallest_group_index] += size

    return groups

def main(dir_names, n, tmp_dir):
    # Create tmp directory if it doesn't exist
    os.makedirs(tmp_dir, exist_ok=True)

    # Get all file sizes
    file_sizes = get_file_sizes(dir_names)
    
    # Distribute files into N groups with roughly equal total size
    groups = distribute_files(file_sizes, n)
    
    # Save filenames to tmp directory
    for i, group in enumerate(groups):
        with open(os.path.join(tmp_dir, f"results_filenames_{i+1}.txt"), "w") as f:
            for file in group:
                f.write(file + "\n")

    # Print out the groups
    for i, group in enumerate(groups):
        total_size = sum(os.path.getsize(file) for file in group)
        if total_size >= 1024 * 1024 * 1024:
            print(f"Group {i + 1:<4} ({total_size / (1024 * 1024 * 1024):.2f} GB)")
        elif total_size >= 1024 * 1024:
            print(f"Group {i + 1:<4} ({total_size / (1024 * 1024):.2f} MB)")
        else:
            print(f"Group {i + 1:<4} ({total_size / 1024:.2f} KB)")

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description='Group files based on size')
    parser.add_argument('--directories', nargs='+', help='List of directories to group files from')
    parser.add_argument('--N', type=int, help='Number of groups to distribute files into')
    parser.add_argument('--tmp', type=str, help='Temporary directory to save group files')
    args = parser.parse_args()
    
    main(args.directories, args.N, args.tmp)