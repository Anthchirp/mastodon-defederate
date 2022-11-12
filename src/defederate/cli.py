import argparse
import functools
import sys
from typing import Callable, Dict, List

import defederate
import defederate.blocklist_parsers


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


def cli_show(cmd_args: List[str]):
    bl_parser: Dict[str, Callable] = {
        "3": defederate.blocklist_parsers.parse_mastodon3,
        "4": defederate.blocklist_parsers.parse_mastodon4,
        "markdown": functools.partial(
            defederate.blocklist_parsers.parse_markdown, "markdown"
        ),
    }
    parser = argparse.ArgumentParser(
        description="Show active instance blocks", prog="defederate show"
    )
    parser.add_argument(
        "--mastodon-version",
        choices=sorted(bl_parser),
        required=True,
        help="Specify the version of Mastodon running on this server",
    )
    parser.add_argument("host", help="The base URL for the server")

    args = parser.parse_args(cmd_args)
    blockset = bl_parser[args.mastodon_version](args.host)
    blocklist = sorted(
        " {entry.level.name}: {entry.server}{due}".format(
            entry=entry, due=f"  due to {entry.reason}" if entry.reason else ""
        )
        for entry in blockset
    )
    print(f"Current blocklist on {args.host}:")
    print("\n".join(blocklist))


def cli_block(args):
    exit("Adding blocks is not yet supported")
