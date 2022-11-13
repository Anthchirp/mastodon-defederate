import json
import urllib.parse
from typing import Set

import requests

from defederate.activitypub import get_nodeinfo
from defederate.const import BlockDef, BlockLevel
from defederate.errors import CannotScrapePage
from defederate.plugin import ServerPlugin


class Mastodon4Server(ServerPlugin):
    def __init__(self, url: str):
        self._server = urllib.parse.urlparse(url)

    @staticmethod
    def understands(url: str) -> bool:
        parsed = urllib.parse.urlparse(url)
        if parsed.path not in ("", "/"):
            return False
        nodeinfo = get_nodeinfo(url)
        if nodeinfo.get("software", {}).get("name") != "mastodon":
            return False
        return nodeinfo["software"].get("version", "").startswith("4.")

    def get_public_blocklist(self) -> Set[BlockDef]:
        url = self._server._replace(
            path="/api/v1/instance/domain_blocks", params="", query="", fragment=""
        ).geturl()
        response = requests.get(url)
        if response.status_code != 200:
            raise CannotScrapePage(
                f"Server at {self._server.netloc} returned {response.status_code}: {response.reason}"
            )
        levels = {"suspend": BlockLevel.SUSPEND, "silence": BlockLevel.SILENCE}
        return {
            BlockDef(
                source=self._server.netloc,
                server=entry["domain"],
                digest=entry["digest"],
                level=levels.get(entry["severity"], BlockLevel.NONE),
                reason=entry["comment"] or "",
            )
            for entry in json.loads(response.text)
        }
