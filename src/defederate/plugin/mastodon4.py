import json
from typing import Set

import requests

from defederate.const import BlockDef, BlockLevel
from defederate.errors import CannotScrapePage
from defederate.plugin import ServerPlugin


class Mastodon4Server(ServerPlugin):
    def __init__(self, server: str):
        self._server = server

    def get_public_blocklist(self) -> Set[BlockDef]:
        url = f"https://{self._server}/api/v1/instance/domain_blocks"
        exit("failo")
        response = requests.get(url)
        if response.status_code != 200:
            raise CannotScrapePage(
                f"Server at {url} returned {response.status_code}: {response.reason}"
            )
        levels = {"suspend": BlockLevel.SUSPEND, "silence": BlockLevel.SILENCE}
        return {
            BlockDef(
                source=self._server,
                server=entry["domain"],
                digest=entry["digest"],
                level=levels.get(entry["severity"], BlockLevel.NONE),
                reason=entry["comment"] or "",
            )
            for entry in json.loads(response.text)
        }
