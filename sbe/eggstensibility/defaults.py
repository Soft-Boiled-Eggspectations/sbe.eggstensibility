"""
sbe.eggstensibility.defaults provides the default implementation for the protocols
defined in sbe.eggstensibility.protocols, allowing the user to set-up an opinionated
system to load external extensions.
"""

from typing import TypeAlias


# These are redefines to ease importing the specific classes.
from ._internal.description import (
    DefaultDescription as Description,
    ExtensionID as ExtensionID,
)

from ._internal.resolver import (
    DefaultDirectoryModuleResolver as DirectoryModuleResolver,  # noqa: F401
)
from ._internal.resolver import (
    DefaultFileModuleResolver as FileModuleResolver,  # noqa: F401
    DefaultDescriptionResolver as _DefaultDescriptionResolver,
)

from ._internal.order import (
    DefaultResolveIdentifier as ResolveIdentifier,  # noqa: F401
    DefaultResolveDependency as ResolveDependency,  # noqa: F401
    OrderExtensionDescriptions as _OrderExtensionDescriptions,
)


DescriptionResolver: TypeAlias = _DefaultDescriptionResolver[Description]
OrderExtensionDescriptions: TypeAlias = _OrderExtensionDescriptions[
    Description, ExtensionID
]
