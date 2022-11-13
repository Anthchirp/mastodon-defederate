from abc import ABC, abstractmethod
from typing import List, Set, Type

from importlib_metadata import EntryPoint, entry_points

from defederate.const import BlockDef


class ServerPlugin(ABC):
    @abstractmethod
    def __init__(self, server: str):
        ...

    def get_public_blocklist(self) -> Set[BlockDef]:
        raise NotImplementedError("This function is not supported by this server type")

    @staticmethod
    def understands(url: str) -> bool:
        return False


def list_server_plugins() -> List[EntryPoint]:
    try:
        return entry_points()["defederate.plugin.server"]
    except KeyError:
        raise RuntimeError(
            "Entry points missing. Defederation package is not installed correctly."
        )


def get_server_plugin(name: str) -> Type[ServerPlugin]:
    plugin = [
        ep for ep in entry_points()["defederate.plugin.server"] if ep.name == name
    ]
    if not plugin:
        raise KeyError(f"Could not find plugin {name}")
    if len(plugin) > 1:
        raise KeyError(f"Plugin {name} is ambiguous")
    entry_point = plugin[0].load()
    if not issubclass(entry_point, ServerPlugin):
        raise TypeError(
            f"Plugin {name} is invalid - returned {entry_point}, not ServerPlugin object"
        )
    return entry_point
