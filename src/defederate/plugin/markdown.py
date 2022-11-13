import re
import urllib.parse
from typing import Set

import requests

from defederate.const import BlockDef, BlockLevel
from defederate.errors import CannotScrapePage
from defederate.plugin import ServerPlugin

_table_parser = re.compile(
    r"^\|(?P<server>[^|]+)\|\s*(?P<mark>[^ |]+)\s*\|\s*(?P<reason>[^|]*)\|",
    re.MULTILINE,
)


class MarkdownServer(ServerPlugin):
    def __init__(self, server: str):
        self._server = server

    @staticmethod
    def understands(url: str) -> bool:
        parsed = urllib.parse.urlparse(url)
        return parsed.path[-3:].upper() == ".MD"

    def get_public_blocklist(self) -> Set[BlockDef]:
        url = self._server
        response = requests.get(url)
        if response.status_code != 200:
            raise CannotScrapePage(
                f"Server at {url} returned {response.status_code}: {response.reason}"
            )
        levels = {
            "\N{NO ENTRY}": BlockLevel.SUSPEND,
            "\N{SPEAKER WITH CANCELLATION STROKE}": BlockLevel.SILENCE,
        }

        blocks: Set[BlockDef] = set()
        for line in response.text.split("\n"):
            definition = _table_parser.match(line)
            if definition:
                servers, mark, reason = definition.groups()
                for server in servers.split(","):
                    if "." not in server:
                        continue
                    blocks.add(
                        BlockDef(
                            source=self._server,
                            server=server.strip(),
                            level=levels.get(mark, BlockLevel.NONE),
                            reason=reason.strip(),
                        )
                    )
        return blocks
