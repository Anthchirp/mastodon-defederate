import functools
import json
import urllib.parse
from typing import Optional

import requests


@functools.lru_cache(maxsize=None)
def get_nodeinfo(url: str) -> dict:
    parsed_url = urllib.parse.urlparse(url)
    well_known_nodeinfo = parsed_url._replace(
        path="/.well-known/nodeinfo", params="", query="", fragment=""
    )
    ap_nodeinfo = requests.get(well_known_nodeinfo.geturl())
    if ap_nodeinfo.status_code != 200:
        return {}
    ap_nodeinfo_data = json.loads(ap_nodeinfo.text)
    nodeinfo_url: Optional[str] = None
    for entry in ap_nodeinfo_data.get("links", []):
        if entry.get("rel") == "http://nodeinfo.diaspora.software/ns/schema/2.0":
            nodeinfo_url = entry.get("href")
            break
    if not nodeinfo_url:
        return {}

    nodeinfo = requests.get(nodeinfo_url)
    if nodeinfo.status_code != 200:
        return {}
    nodeinfo_data = json.loads(nodeinfo.text)
    if not isinstance(nodeinfo_data, dict):
        return {}
    return nodeinfo_data
