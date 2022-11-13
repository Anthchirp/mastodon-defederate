import argparse
import sys
import urllib.parse
from typing import List

import defederate
import defederate.blocklist_parsers
import defederate.plugin


def _sanitize_address(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme and not parsed.netloc:
        parsed = urllib.parse.urlparse("https://" + url)
    return parsed.geturl()


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
    known_server_types: List[str] = sorted(
        ep.name for ep in defederate.plugin.list_server_plugins()
    )
    parser = argparse.ArgumentParser(
        description="Show active instance blocks", prog="defederate show"
    )
    parser.add_argument(
        "--mastodon-version",
        choices=known_server_types,
        help="Specify the version of Mastodon running on this server",
    )
    parser.add_argument(
        "host", help="The base URL for the server", type=_sanitize_address
    )

    args = parser.parse_args(cmd_args)
    if not args.mastodon_version:
        accepting_plugins = sorted(
            server_type
            for server_type in known_server_types
            if defederate.plugin.get_server_plugin(server_type).understands(args.host)
        )
        if not accepting_plugins:
            exit(
                "Could not identify the server type. Please specify --mastodon-version"
            )
        if len(accepting_plugins) > 1:
            exit(
                f"Could not identify the server type. Please specify --mastodon-version with one of {accepting_plugins}"
            )
        args.mastodon_version = accepting_plugins[0]
        print(f"Autodetected server type {args.mastodon_version}")

    server = defederate.plugin.get_server_plugin(args.mastodon_version)(args.host)
    blockset = server.get_public_blocklist()
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
