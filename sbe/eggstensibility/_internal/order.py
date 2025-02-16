"""
sbe.eggstensibility.order provides the default order logic.
"""

from typing import Generic, Iterable, Protocol, TypeVar

import networkx as nx  # type: ignore

from ..exceptions import CircularDependencyException, MissingDependencyException
from .description import DefaultDescription, ExtensionID

ResolveIdentifierDescriptionT = TypeVar(
    "ResolveIdentifierDescriptionT", contravariant=True
)
ResolveIdentifierDescriptionIdentifierT = TypeVar(
    "ResolveIdentifierDescriptionIdentifierT", covariant=True
)


class ResolveIdentifier(
    Protocol,
    Generic[ResolveIdentifierDescriptionT, ResolveIdentifierDescriptionIdentifierT],
):
    """
    ResolveIdentifier retrieves the unique identifier of a given extension description.
    """

    def __call__(
        self, description: ResolveIdentifierDescriptionT
    ) -> ResolveIdentifierDescriptionIdentifierT:
        """
        Resolve the identifier of a specific description.

        Args:
            description (ResolveIdentifierDescriptionT):
                The description to obtain the identifier from.

        Returns:
            ResolveIdentifierDescriptionIdentifierT:
                The identifier associated with the description.
        """


class DefaultResolveIdentifier:
    """
    ResolveIdentifier retrieves the unique identifier of a given extension description
    by returning it's `extension_id` property.
    """

    def __call__(self, description: DefaultDescription) -> ExtensionID:
        """
        Resolve the identifier of a specific description.

        Args:
            description (DefaultDescription): The description to obtain the identifier from.

        Returns:
            ExtensionID: The identifier associated with the description.
        """
        return description.extension_id


ResolveDependencyDescriptionT = TypeVar(
    "ResolveDependencyDescriptionT", contravariant=True
)
ResolveDependencyDescriptionIdentifierT = TypeVar(
    "ResolveDependencyDescriptionIdentifierT", covariant=True
)


class ResolveDependency(
    Protocol,
    Generic[ResolveDependencyDescriptionT, ResolveDependencyDescriptionIdentifierT],
):
    """
    ResolveDependency retrieves the dependencies of a given extension description.
    """

    def __call__(
        self, description: ResolveDependencyDescriptionT
    ) -> Iterable[ResolveDependencyDescriptionIdentifierT]:
        """
        Resolve the unique identifier of the dependencies of a specific description.

        Args:
            description (ResolveDependencyDefaultDescription):
                The description to obtain the dependencies from.

        Returns:
            Iterable[ResolveDependencyExtensionID]:
                The identifiers of the dependencies.
        """


class DefaultResolveDependency:
    """
    ResolveDependency retrieves the unique identifiers of the dependencies of a given
    extension description by returning it's `dependencies` property.
    """

    def __call__(self, description: DefaultDescription) -> Iterable[ExtensionID]:
        """
        Resolve the unique identifier of the dependencies of a specific description.

        Args:
            description (DefaultDescription): The description to obtain the dependencies from.

        Returns:
            Iterable[ExtensionID]: The identifiers of the dependencies.
        """
        return description.dependencies


DescriptionT = TypeVar("DescriptionT")
DescriptionIdentifierT = TypeVar("DescriptionIdentifierT")


class OrderExtensionDescriptions(Generic[DescriptionT, DescriptionIdentifierT]):
    """
    OrderExtensionDescriptions is responsible for ordering the descriptions based upon their
    dependencies.
    """

    def __init__(
        self,
        description_identifier_resolver: ResolveIdentifier[
            DescriptionT, DescriptionIdentifierT
        ],
        description_dependency_resolver: ResolveDependency[
            DescriptionT, DescriptionIdentifierT
        ],
    ) -> None:
        """
        Create a new DefaultOrderExtensionDescriptions.

        Args:
            description_identifier_resolver (ResolveIdentifier):
                The resolver used to retrieve the unique identifier of a provided
                extension description
            description_dependency_resolver (ResolveDependency):
                The resolver used to retrieve the extensions descriptions that a given
                extension description relies on.
        """
        self._identifier_resolver = description_identifier_resolver
        self._dependency_resolver = description_dependency_resolver

    def __call__(
        self, extension_descriptions: Iterable[DescriptionT]
    ) -> Iterable[DescriptionT]:
        """
        Order the provided extension_descriptions based on their dependencies.

        Args:
            extension_descriptions (Iterable[DescriptionT]):
                The extension descriptions to sort

        Returns:
            Iterable[DescriptionT]: The ordered description based on their dependencies
        """
        descriptions = list(extension_descriptions)
        available_extension_ids = {
            self._identifier_resolver(description) for description in descriptions
        }
        required_ids = {
            extension_id
            for description in descriptions
            for extension_id in self._dependency_resolver(description)
        }

        if not required_ids.issubset(available_extension_ids):
            raise MissingDependencyException(
                "The set of dependency descriptions is not a subset of the provided descriptions."
            )

        dag = nx.DiGraph()

        description_map = dict()

        for description in descriptions:
            description_id = self._identifier_resolver(description)
            description_map[description_id] = description
            dag.add_node(description_id)

        for description in descriptions:
            extension_id = self._identifier_resolver(description)
            if deps := list(self._dependency_resolver(description)):
                dag.add_edges_from(((dep_id, extension_id) for dep_id in deps))

        if not nx.is_directed_acyclic_graph(dag):
            raise CircularDependencyException(
                "There is a circular dependency in the provided extension descriptions.",
                descriptions,
            )

        return [description_map[n] for n in nx.topological_sort(dag)]
