import argparse
import sys

import defederate


def main():
    parser = argparse.ArgumentParser(
        usage="defederate <command> [<args>]",
        description="""Tools for Mastodon Instance Blocklist Management (v{version})
The most commonly used commands are:
   show     Show currently active instance blocks
   block    Add an instance block
Each command has its own set of parameters, and you can get more information
by running defederate <command> --help
""".format(
            version=defederate.__version__
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("subcommand", help=argparse.SUPPRESS)
    # parse_args defaults to [1:] for args, but need to
    # exclude the rest of the args too, or validation will fail
    parameters = sys.argv[1:2]
    if not parameters:
        parser.print_help()
        sys.exit(0)
    args = parser.parse_args(parameters)
    subcommand = globals().get("cli_" + args.subcommand)
    if subcommand:
        return subcommand(sys.argv[2:])
    parser.print_help()
    print()
    sys.exit(f"Unrecognized command: {args.subcommand}")


def cli_show(args):
    print("Show", args)


def cli_block(args):
    print("Block", args)
