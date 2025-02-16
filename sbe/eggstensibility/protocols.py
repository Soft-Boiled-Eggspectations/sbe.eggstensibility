"""
sbe.eggstensibility.protocols defines the interface contracts used within this library.
"""

from ._internal.order import ResolveIdentifier as ResolveIdentifier
from ._internal.order import ResolveDependency as ResolveDependency

from ._internal.resolver import ModuleResolver as ModuleResolver
from ._internal.resolver import DescriptionResolver as DescriptionResolver

from ._internal.logging import Logger as Logger
