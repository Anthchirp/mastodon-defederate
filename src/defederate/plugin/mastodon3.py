import re
import urllib.parse
from typing import Set

import requests

from defederate.activitypub import get_nodeinfo
from defederate.const import BlockDef, BlockLevel
from defederate.errors import CannotScrapePage
from defederate.plugin import ServerPlugin


class Mastodon3Server(ServerPlugin):
    def __init__(self, server: str):
        self._server = urllib.parse.urlparse(server)

    @staticmethod
    def understands(url: str) -> bool:
        parsed = urllib.parse.urlparse(url)
        if parsed.path not in ("", "/"):
            return False
        nodeinfo = get_nodeinfo(url)
        if nodeinfo.get("software", {}).get("name") != "mastodon":
            return False
        return nodeinfo["software"].get("version", "").startswith("3.")

    def get_public_blocklist(self) -> Set[BlockDef]:
        url = self._server._replace(
            path="/about/more", params="", query="", fragment=""
        ).geturl()
        response = requests.get(url)
        if response.status_code != 200:
            raise CannotScrapePage(
                f"Server at {self._server.netloc} returned {response.status_code}: {response.reason}"
            )

        start = re.split(r"<h. id='unavailable-content'>", response.text, maxsplit=1)
        if len(start) < 2:
            raise CannotScrapePage(
                f"Server at {self._server.netloc} returned page in unexpected format"
            )
        server_list = start[1]
        results = set()

        limited = re.search(
            r"<h.>Limited servers(.*?)</table>", server_list, re.IGNORECASE | re.DOTALL
        )
        suspended = re.search(
            r"<h.>Suspended servers(.*?)</table>",
            server_list,
            re.IGNORECASE | re.DOTALL,
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
                        source=self._server.netloc,
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
