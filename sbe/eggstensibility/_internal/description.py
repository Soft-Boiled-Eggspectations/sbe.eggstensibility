"""
sbe.eggstensibility.extension.description defines the default description for resolving
extensions.
"""

from functools import cache
from typing import Callable, Generic, Iterable, TypeAlias, TypeVar, Union

from uuid import uuid4


# By default the ids of internal plugins use a hex representation of a uuid
ExtensionID: TypeAlias = str


ExtensionT = TypeVar("ExtensionT")


class DefaultDescription(Generic[ExtensionT]):
    """
    DefaultDescription defines a default description for extensions within
    eggstensibility.

    eggstensibility does not require the consumer to use DefaultDescriptions and allows
    for custom definitions
    """

    def __init__(
        self,
        name: str,
        extension_ctor: Callable[[], ExtensionT],
        dependencies: Union[
            Iterable[ExtensionID], Callable[[], Iterable[ExtensionID]], None
        ] = None,
    ) -> None:
        """
        Create a new DefaultDescription with the given name and dependencies.

        Args:
            name (str):
                The (human-readable) name of this extension
            dependencies (Iterable[ExtensionID] | Callable[[], Iterable[ExtensionID]]):
                The dependencies of this extension.
        """
        self._name = name
        self._id = hex(uuid4().int)
        self._extension_ctor = extension_ctor
        self._dependencies = dependencies if dependencies is not None else []

    @property
    def name(self) -> str:
        """The (human-readable) name of this extension."""
        return self._name

    @property
    def extension_id(self) -> ExtensionID:
        """The unique id of this extension."""
        return self._id

    @property
    def dependencies(self) -> Iterable[ExtensionID]:
        """The dependencies of this extension."""
        return iter(self._resolve_dependencies())

    def create_extension(self) -> ExtensionT:
        """Create the extension described by this description."""
        return self._extension_ctor()

    @cache
    def _resolve_dependencies(self) -> Iterable[ExtensionID]:
        return set(
            self._dependencies() if callable(self._dependencies) else self._dependencies
        )
