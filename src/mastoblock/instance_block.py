import re
import typing
import urllib.parse

import requests

from .update_blocklist import Blocklevel


class BlockSubmission(typing.NamedTuple):
    domain: str
    severity: Blocklevel
    reject_media: bool = False
    reject_reports: bool = False
    obfuscate: bool = False
    private_comment: str = ""
    public_comment: str = ""


class CannotScrapePage(RuntimeError):
    pass


def cookie_decode(input: str) -> str:
    if "%" in input:
        return urllib.parse.unquote(input)
    return input


class Mastodon3Web:
    def __init__(self, server_url, mastodon_session, session_id):
        self._mastodon_session = cookie_decode(mastodon_session)
        self._session_id = cookie_decode(session_id)
        self._server_url = server_url.rstrip("/")

    def add(self, block: BlockSubmission):
        cookies = {
            "_mastodon_session": self._mastodon_session,
            "_session_id": self._session_id,
        }
        headers = {"User-Agent": "Mozilla/5.0", "Accept_Language": "en-US,en;q=0.5"}
        new_page = f"{self._server_url}/admin/domain_blocks/new"
        response = requests.get(new_page, cookies=cookies, headers=headers)

        csrf = re.search(
            r'<meta name="csrf-token" content="([^"]*)"', response.text, re.DOTALL
        )
        if not csrf:
            raise CannotScrapePage("Could not find CSRF token on domain block page")
        headers["X-CSRF-Token"] = csrf.group(1)

        form = re.search(r"(<form(.*?)</form>)", response.text, re.DOTALL)
        if not form:
            raise CannotScrapePage("Could not identify form on domain block page")
        auth_match = re.search(
            r'<input [^>]*name="authenticity_token"[^>]*value="([^"]+)"',
            form.group(1),
            re.DOTALL,
        )
        if not auth_match:
            raise CannotScrapePage("Could not find authentication token on page")

        payload = {
            "authenticity_token": auth_match.group(1),
            "domain_block[domain]": block.domain,
            "domain_block[reject_media]": "1" if block.reject_media else "0",
            "domain_block[reject_reports]": "1" if block.reject_reports else "0",
            "domain_block[obfuscate]": "1" if block.obfuscate else "0",
            "domain_block[private_comment]": block.private_comment,
            "domain_block[public_comment]": block.public_comment,
            "button": "",
        }
        if block.severity is Blocklevel.SUSPEND:
            payload["domain_block[severity]"] = "suspend"
        elif block.severity is Blocklevel.SILENCE:
            payload["domain_block[severity]"] = "silence"
        else:
            payload["domain_block[severity]"] = "noop"

        block_response = requests.post(
            f"{self._server_url}/admin/domain_blocks",
            cookies=response.cookies,
            data=payload,
            headers=headers,
        )
        if block_response.status_code == 200:
            return
        raise CannotScrapePage(
            f"Server returned {block_response.status_code}: {block_response.reason}"
        )


mw = Mastodon3Web(
    "https://mast.uxp.de",
    "mastodon session goes here",
    "session id goes here",
)

mw.add(
    BlockSubmission(
        "beefyboys.club",
        severity=Blocklevel.SUSPEND,
        public_comment="test suspension :)",
    )
)
