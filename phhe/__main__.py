import argparse
from .parse import parse_file


argument_parser = argparse.ArgumentParser(
    description="Used to compile phhe code",  # TODO we need a name for the language
    epilog="Created by conner, Lorxu & xedre"
)

argument_parser.add_argument(
    "file",
    action="store",
    help="the file to compile"
)

# TODO setup a default for the destination (need to agree on file extensions first)
argument_parser.add_argument(
    "dest",
    action="store",
    help="the destination file"
)

arguments = argument_parser.parse_args()

# Load the file in and interpret it
path = arguments.file
tree = parse_file(path)
print(tree.eval())