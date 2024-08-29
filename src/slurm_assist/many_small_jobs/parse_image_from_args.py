# This script grabs the container image and passes it on first, followed by all other arguments.

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--container-image', type=str)
args, unknown_args = parser.parse_known_args()
print(args.container_image)