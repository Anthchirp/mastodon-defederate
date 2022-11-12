import enum
from typing import NamedTuple, Optional


class BlockLevel(enum.IntEnum):
    NONE = enum.auto()
    SILENCE = enum.auto()
    SUSPEND = enum.auto()


class BlockSubmission(NamedTuple):
    domain: str
    severity: BlockLevel
    reject_media: bool = False
    reject_reports: bool = False
    obfuscate: bool = False
    private_comment: str = ""
    public_comment: str = ""


class BlockDef(NamedTuple):
    source: str
    server: str
    level: BlockLevel
    reason: str
    digest: Optional[str] = None
