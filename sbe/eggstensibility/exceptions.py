"""
sbe.eggstensibility.exceptions provides the common exceptions used within
eggstensibility.
"""

from pathlib import Path


class BaseEggstensibilityException(Exception):
    """
    BaseEggstensibilityException is the base exception of all exceptions
    within eggstensibility.
    """


class EggstensibilityPathException(BaseEggstensibilityException):
    """
    EggstensibilityPathException is the base-exception for any Path-related
    exceptions within eggstensibility.
    """

    def __init__(self, message: str, path: Path):
        """
        Create a new EggstensibilityPathException with the given message and
        Path causing the exception.

        Args:
            message (str): The error-message
            path: (Path): The path causing the issue.
        """
        super().__init__(message)
        self._path = path

    @property
    def path(self) -> Path:
        """The path causing the issue."""
        return self._path

    def __str__(self):
        return f"{self.args[0]} (Path: {self.path})"


class InvalidPathException(EggstensibilityPathException):
    """Exception thrown when an invalid path is encountered."""


class NonExistentPathException(EggstensibilityPathException):
    """Exception thrown when the provided path does not exist on the filesystem."""


class EggstensibilityDependencyException(BaseEggstensibilityException):
    """
    EggstensibilityDependencyException is the base exception for any dependency-related
    exceptions within eggstensibility.
    """


class CircularDependencyException(EggstensibilityDependencyException):
    """
    CircularDependencyException is thrown when the provided extensions contain a
    circular dependency.
    """

    def __init__(self, message: str, descriptions: list):
        """
        Create a new Circular dependency exception with the given message and all of
        the provided dependencies that caused the exception.

        The exact types of the descriptions depends on the descriptions used to provide
        to the load mechanism.

        Args:
            message (str): The exception message
            dependencies (list): The dependencies that caused the circular exception
        """

        super().__init__(message)
        self._descriptions = descriptions

    @property
    def descriptions(self) -> list:
        """The descriptions involved in the circular dependency."""
        return list(self._descriptions)


class MissingDependencyException(EggstensibilityDependencyException):
    """
    MissingDependencyException is thrown when the provided extensions
    require other extensions that are not available.
    """


class IncompleteLoaderConfigurationException(BaseEggstensibilityException):
    """
    IncompleteLoaderConfigurationException is thrown when the builder tries to build
    a loader with an incomplete configuration.
    """
