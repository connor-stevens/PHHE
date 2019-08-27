import argparse
from .parse import parse_file, Context
from .codegen import codegen


argument_parser = argparse.ArgumentParser(
    # TODO we need a name for the language
    description="Used to compile phhe code",
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

# Generate C and save it to 'dest'
dest_path = arguments.dest
dest = open(dest_path, 'w')
dest.write(str(codegen([tree])))

# And print the evaluated result
ret = tree.eval(Context())
if ret is not None:
    print(ret)
