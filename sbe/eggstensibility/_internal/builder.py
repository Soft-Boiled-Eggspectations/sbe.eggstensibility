"""
sbe.eggstensibility.builder defines all of the internal builder to construct the loader
of the eggstensibility library.
"""

from __future__ import annotations

from pathlib import Path
from typing import Generic, Iterable, List, Optional, Protocol, Sequence, TypeVar

from sbe.eggstensibility import exceptions

from .logging import Logger
from .resolver import DescriptionResolver, ModuleResolver
from .order import OrderExtensionDescriptions, ResolveIdentifier, ResolveDependency


LoaderDescriptionT = TypeVar("LoaderDescriptionT", covariant=True)
LoaderDescriptionIdentifierT = TypeVar("LoaderDescriptionIdentifierT", covariant=True)


class Loader(Protocol, Generic[LoaderDescriptionT]):
    """The Loader created with a Builder used to load all the extension descriptions."""

    def load_extension_descriptions(self) -> Iterable[LoaderDescriptionT]:
        """
        Load and return an ordered list of the descriptions describing the extensions.

        The descriptions are ordered based upon their dependencies. If they have no
        dependencies no guarantees are given about their order.

        Returns:
            Iterable[DescriptionT]: The descriptions ordered by their dependencies.
        """


BuilderDescriptionT = TypeVar("BuilderDescriptionT")
BuilderDescriptionIdentifierT = TypeVar(
    "BuilderDescriptionIdentifierT", contravariant=True
)


class Builder(Protocol, Generic[BuilderDescriptionT, BuilderDescriptionIdentifierT]):
    """The builder provided to the user to build up the eggstensibility loader."""

    def build(self) -> Loader:
        """
        Build the loader based upon the configuration.

        Returns:
            Loader: The loader constructed with the specified configuration.

        Exceptions:
            IncompleteLoaderConfigurationException:
                Thrown when the loader is considered incomplete.

            Currently this occurs when the following have not been called at least once:
            * configure_identifier_resolver
            * configure_dependency_resolver
        """

    def configure_logger(self, logger: Logger) -> Builder:
        """
        Define a logger used when loading the descriptions.

        If never called, no logging will occur. If called twice the last configured
        logger will be used.

        Args:
            logger (Logger): The logger to use in the constructed loader.

        Returns:
            Builder: This builder.
        """

    def add_module_resolver(self, resolver: ModuleResolver) -> Builder:
        """
        Add the specified ModuleResolver resolver to the Loader.

        If never called, no modules will be resolved. If called multiple times the
        provided paths are handled by each module_resolver, thus a path could yield
        multiple actual modules created by different resolvers. It is left up to the
        user to handle these situations.

        Args:
            resolver (ModuleResolver): The ModuleResolver to add to the loader.

        Returns:
            Builder: This builder.
        """

    def add_description_resolver(
        self, resolver: DescriptionResolver[BuilderDescriptionT]
    ) -> Builder:
        """
        Add the specified DescriptionResolver resolver to the Loader.

        If never called, no descriptions will be retrieved by the Loader. If
        provided multiple times all of the paths created by the ModuleResolvers
        will be evaluated by each of the DescriptionResolvers. It is left up to the
        user to handle these situations.

        Args:
            resolver (DescriptionResolver[DescriptionT]): The DescriptionResolver to add to the loader.

        Returns:
            Builder: This builder
        """

    def add_harvest_path(self, *path: Path) -> Builder:
        """
        Add the specified harvest path to the Loader which will be harvested upon
        calling `load` of the created Loader.

        Args:
            *path (Path): The paths to be added.
        """

    def configure_identifier_resolver(
        self,
        resolver: ResolveIdentifier[BuilderDescriptionT, BuilderDescriptionIdentifierT],
    ) -> Builder:
        """
        Configure the specified resolver to be used as the identifier resolver.

        This function needs to be called at least once before calling `build`. If it
        is called multiple times, only the resolver in the last call will be used.

        Args:
            resolver (ResolveIdentifier): The resolver used to obtain identifiers of descriptions.
        """

    def configure_dependency_resolver(
        self,
        resolver: ResolveDependency[BuilderDescriptionT, BuilderDescriptionIdentifierT],
    ) -> Builder:
        """
        Configure the specified resolver to be used as the dependency resolver.

        This function needs to be called at least once before calling `build`. If it
        is called multiple times, only the resolver in the last call will be used.

        Args:
            resolver (ResolveDependency): The resolver used to obtain dependencies of descriptions.
        """


class _Loader(Generic[LoaderDescriptionT, LoaderDescriptionIdentifierT]):
    def __init__(
        self,
        identifier_resolver: ResolveIdentifier[
            LoaderDescriptionT, LoaderDescriptionIdentifierT
        ],
        dependency_resolver: ResolveDependency[
            LoaderDescriptionT, LoaderDescriptionIdentifierT
        ],
        harvest_paths: Sequence[Path],
        module_resolvers: Sequence[ModuleResolver],
        description_resolvers: Sequence[DescriptionResolver],
    ) -> None:
        self._identifier_resolver = identifier_resolver
        self._dependency_resolver = dependency_resolver
        self._harvest_paths = harvest_paths
        self._module_resolvers = module_resolvers
        self._description_resolvers = description_resolvers

    def _harvest_valid_modules(self) -> Iterable[Path]:
        for path in self._harvest_paths:
            for resolver in self._module_resolvers:
                yield from resolver(path)

    def _retrieve_descriptions(
        self, module_paths: List[Path]
    ) -> Iterable[LoaderDescriptionT]:
        for resolver in self._description_resolvers:
            yield from resolver(iter(module_paths))

    def load_extension_descriptions(self) -> Sequence[LoaderDescriptionT]:
        module_paths = list(self._harvest_valid_modules())
        descriptions = list(self._retrieve_descriptions(module_paths))

        order_operation = OrderExtensionDescriptions[
            LoaderDescriptionT, LoaderDescriptionIdentifierT
        ](self._identifier_resolver, self._dependency_resolver)
        return list(order_operation(iter(descriptions)))


class _Builder(Generic[BuilderDescriptionT, BuilderDescriptionIdentifierT]):
    def __init__(self) -> None:
        self._logger: Optional[Logger] = None
        self._module_resolvers: List[ModuleResolver] = []
        self._description_resolvers: List[DescriptionResolver] = []
        self._harvest_paths: List[Path] = []

        self._identifier_resolver: Optional[ResolveIdentifier] = None
        self._dependency_resolver: Optional[ResolveDependency] = None

    def build(self) -> Loader:
        if self._identifier_resolver is None:
            raise exceptions.IncompleteLoaderConfigurationException(
                f"No '{ResolveIdentifier.__name__}' provided."
            )
        if self._dependency_resolver is None:
            raise exceptions.IncompleteLoaderConfigurationException(
                f"No '{ResolveDependency.__name__}' provided."
            )

        return _Loader(
            self._identifier_resolver,
            self._dependency_resolver,
            self._harvest_paths,
            self._module_resolvers,
            self._description_resolvers,
        )

    def configure_logger(self, logger: Logger) -> Builder:
        self._logger = logger
        return self

    def add_module_resolver(self, resolver: ModuleResolver) -> Builder:
        self._module_resolvers.append(resolver)
        return self

    def add_description_resolver(
        self, resolver: DescriptionResolver[BuilderDescriptionT]
    ) -> Builder:
        self._description_resolvers.append(resolver)
        return self

    def add_harvest_path(self, *path: Path) -> Builder:
        self._harvest_paths.extend(path)
        return self

    def configure_identifier_resolver(
        self,
        resolver: ResolveIdentifier[BuilderDescriptionT, BuilderDescriptionIdentifierT],
    ) -> Builder:
        self._identifier_resolver = resolver
        return self

    def configure_dependency_resolver(
        self,
        resolver: ResolveDependency[BuilderDescriptionT, BuilderDescriptionIdentifierT],
    ) -> Builder:
        self._dependency_resolver = resolver
        return self


def construct_builder() -> Builder[BuilderDescriptionT, BuilderDescriptionIdentifierT]:
    """
    Create a new Builder to configure the appropriate Loader.
    """
    return _Builder()
