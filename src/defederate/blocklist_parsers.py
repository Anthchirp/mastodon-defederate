import collections
import hashlib
import json
import os.path
import re
import urllib.request
from typing import Dict, Optional, Set

from .const import BlockDef, BlockLevel

OFFLINE = os.path.exists("mymasto")


def sha256(text: str) -> str:
    m = hashlib.sha256()
    m.update(text.encode("utf8"))
    return m.hexdigest()


def get(url: str) -> str:
    response = urllib.request.urlopen(url)
    data = response.read()
    text = data.decode("utf-8")
    return text


def parse_markdown(source: str, url: str) -> Set[BlockDef]:
    parse = re.compile(
        r"^\|(?P<server>[^|]+)\|\s*(?P<mark>[^ |]+)\s*\|\s*(?P<reason>[^|]*)\|",
        re.MULTILINE,
    )
    if OFFLINE:
        data = open("data").read()
    else:
        data = get(url)
    blocks = set()
    levels = collections.defaultdict(lambda: BlockLevel.NONE)
    levels["\N{NO ENTRY}"] = BlockLevel.SUSPEND
    levels["\N{SPEAKER WITH CANCELLATION STROKE}"] = BlockLevel.SILENCE
    for line in data.split("\n"):
        definition = parse.match(line)
        if definition:
            servers, mark, reason = definition.groups()
            for server in servers.split(","):
                if "." not in server:
                    continue
                blocks.add(
                    BlockDef(
                        source=source,
                        server=server.strip(),
                        level=levels[mark],
                        reason=reason.strip(),
                    )
                )
    return blocks


def parse_mastodon4(server: str, url: Optional[str] = None) -> Set[BlockDef]:
    url = url or f"https://{server}/api/v1/instance/domain_blocks"
    if OFFLINE:
        datastr = open("masto").read()
    else:
        datastr = get(url)
    data = set()
    levels = collections.defaultdict(lambda: BlockLevel.NONE)
    levels["suspend"] = BlockLevel.SUSPEND
    levels["silence"] = BlockLevel.SILENCE
    for entry in json.loads(datastr):
        data.add(
            BlockDef(
                source=server,
                server=entry["domain"],
                digest=entry["digest"],
                level=levels[entry["severity"]],
                reason=entry["comment"] or "",
            )
        )
    return data


def parse_mastodon3(server: str, url: Optional[str] = None) -> Set[BlockDef]:
    url = url or f"https://{server}/about/more"
    results: Set[BlockDef] = set()

    if OFFLINE:
        datastr = open("mymasto").read()
    else:
        datastr = get(url)
    start = re.split(r"<h. id='unavailable-content'>", datastr, maxsplit=1)
    if len(start) < 2:
        return results
    datastr = start[1]

    limited = re.search(
        r"<h.>Limited servers(.*?)</table>", datastr, re.IGNORECASE | re.DOTALL
    )
    suspended = re.search(
        r"<h.>Suspended servers(.*?)</table>", datastr, re.IGNORECASE | re.DOTALL
    )
    blockexpr = re.compile(
        r"<td\s*class[^>]*>\s*<span(?: title='SHA-256: (?P<hash>[a-fA-F0-9]*)')?[^>]*>"
        r"(?P<server>[^<]*)</span>\s*</td>\s*<td[^>]*>(?P<reason>[^<]*)</td>(?P<optional>asdf)?",
        re.IGNORECASE | re.DOTALL,
    )

    def parse_and_add(result_iterator, at_level):
        for entry in result_iterator:
            results.add(
                BlockDef(
                    source=server,
                    server=entry["server"],
                    digest=entry["hash"],
                    level=at_level,
                    reason=entry["reason"].strip(),
                )
            )

    if limited:
        parse_and_add(blockexpr.finditer(limited.group(1)), BlockLevel.SILENCE)
    if suspended:
        parse_and_add(blockexpr.finditer(suspended.group(1)), BlockLevel.SUSPEND)

    return results


if __name__ == "__main__":
    remote_sources = [
        parse_markdown(
            "chaos.social",
            "https://raw.githubusercontent.com/chaossocial/about/07c5d774157b847a796b8b126990277ee1643b66/blocked_instances.md",
        ),
        parse_mastodon4("mas.to"),
    ]
    local_definition = parse_mastodon3("mast.uxp.de")
    exceptions = {
        "birdsite.thorlaksson.com": BlockLevel.SILENCE,  # Twitter-xpost is fine
        "shitpost.cloud": BlockLevel.SILENCE,
    }

    blocklist_remote: Dict[str, BlockDef] = {}
    blocklist_local: Dict[str, BlockDef] = {}
    for source in remote_sources:
        for entry in source:
            digest = entry.digest or sha256(entry.server)
            if digest in blocklist_remote:
                # identify the server name if possible
                if "*" in blocklist_remote[digest].server and "*" not in entry.server:
                    blocklist_remote[digest] = blocklist_remote[digest]._replace(
                        server=entry.server
                    )
                elif "*" not in blocklist_remote[digest].server and "*" in entry.server:
                    entry = entry._replace(server=blocklist_remote[digest].server)
                if blocklist_remote[digest].level >= entry.level:
                    continue  # highest level wins, earlier entry has priority
            if "*" in entry.server and not entry.digest:
                continue  # can't block this
            blocklist_remote[digest] = entry
    for server, level in exceptions.items():
        digest = sha256(server)
        blocklist_remote[digest] = BlockDef(
            source="exception",
            server=server,
            level=level,
            digest=digest,
            reason="manual exception",
        )
    for entry in local_definition:
        if "*" in entry.server and not entry.digest:
            continue  # can't parse this
        digest = entry.digest or sha256(entry.server)
        if digest in blocklist_local and blocklist_local[digest].level <= entry.level:
            continue  # highest level wins
        blocklist_local[digest] = entry

    unseen = blocklist_remote.keys() - blocklist_local.keys()
    unknown = blocklist_local.keys() - blocklist_remote.keys()
    known = blocklist_local.keys() & blocklist_remote.keys()

    if unseen:
        print("\nThe following servers need adding to the blocklist:")
        reasons = sorted(
            "* {server.server} listed on {server.source} as {server.level.name}{dueto}".format(
                server=blocklist_remote[digest],
                dueto=" due to " + blocklist_remote[digest].reason
                if blocklist_remote[digest].reason
                else "",
            )
            for digest in unseen
            if "*" not in blocklist_remote[digest].server
        )
        print("\n".join(reasons))

    if known:
        divergent = sorted(
            (
                "* {local.server} listed locally as {local.level.name} "
                "but is reported as {remote.level.name} on {remote.source}{dueto}"
            ).format(
                local=blocklist_local[digest],
                remote=blocklist_remote[digest],
                dueto=" due to " + blocklist_remote[digest].reason
                if blocklist_remote[digest].reason
                else "",
            )
            for digest in known
            if blocklist_local[digest].level is not blocklist_remote[digest].level
        )
        if divergent:
            print("\nThe following servers need updating:")
            print("\n".join(divergent))

    if unknown:
        print("\nThe following servers are no longer listed and can be removed:")
        reasons = sorted(
            "* {server.server} listed locally as {server.level.name}{dueto}".format(
                server=blocklist_local[digest],
                dueto=" due to " + blocklist_local[digest].reason
                if blocklist_local[digest].reason
                else "",
            )
            for digest in unknown
        )
        print("\n".join(reasons))

    print()
