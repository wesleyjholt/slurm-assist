from slurm_assist import copy_dir_to_remote
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--user', type=str)
parser.add_argument('--host', type=str)
parser.add_argument('--destination-path', type=str)
args = parser.parse_args()

copy_dir_to_remote(
    user=args.user,
    host=args.host,
    destination_path=args.destination_path,
    dir='test_copy_dir_to_remote', 
    ignore_patterns=['dir2/']
)