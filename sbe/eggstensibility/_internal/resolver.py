"""
sbe.eggstensibility.resolver provides the default resolver implementations
"""

import importlib
import importlib.util
import sys
import types

from pathlib import Path
from typing import Generic, Iterable, Optional, Protocol, Sequence, TypeVar

from sbe.eggstensibility._internal.description import DefaultDescription  # noqa: F401


class ModuleResolver(Protocol):
    def __call__(self, path: Path) -> Iterable[Path]:
        """
        Resolve the modules defined in the directory path.

        Args:
            directory_path (Path): The directory to resolve the paths from

        Returns:
            Iterable[Path]: The collection of file paths describing the modules
            with extension points.
        """


class DefaultDirectoryModuleResolver:
    """
    DefaultDirectoryModuleResolver simply resolves names by returning a default
    module_name, e.g. "extension.py" and verifying it exists as a file in
    the provided directory and that this directory is itself a python module.

    The following directory structure is expected:

    <plug-in name>
    ├─── __.init__.py
    ├─── <module_name.py>
    └─── ...
    """

    def __init__(self, module_name: str):
        """
        Create a new DefaultModuleResolver which resolves with the given module_name.

        Args:
            module_name (str):
                The default name of extensions which contain the description of the
                extension point.
        """
        self._module_name = module_name

    @staticmethod
    def _is_valid_directory(prospective_module_path: Path) -> bool:
        return (
            prospective_module_path.is_file()
            and (prospective_module_path.parent / "__init__.py").is_file()
        )

    def __call__(self, directory_path: Path) -> Iterable[Path]:
        """
        Resolve the modules defined in the directory path.

        Args:
            directory_path (Path): The directory to resolve the paths from

        Returns:
            Iterable[Path]: The collection of file paths describing the modules
            with extension points.
        """
        prospective_module_path = (directory_path / self._module_name).resolve()

        if self._is_valid_directory(prospective_module_path):
            yield prospective_module_path


class DefaultFileModuleResolver:
    """
    DefaultFileModuleResolver simply resolves modules by checking if the file exists and
    is a python file. Note that it will not check if the provided module exists within a
    python module directory.

    The following directory structure is expected:

    <parent-name>
    ├─── <provided_module_name.py>
    └─── ...
    """

    @staticmethod
    def _is_valid_directory(prospective_module_path: Path) -> bool:
        return (
            prospective_module_path.is_file()
            and prospective_module_path.suffix == ".py"
        )

    def __call__(self, file_path: Path) -> Iterable[Path]:
        """
        Resolve the modules defined in the directory path.

        Args:
            file_path (Path): The module path to resolve

        Returns:
            Iterable[Path]: The collection of file paths describing the modules
            with extension points.
        """
        prospective_module_path = file_path.resolve()
        if self._is_valid_directory(prospective_module_path):
            yield prospective_module_path


DescriptionT = TypeVar("DescriptionT", covariant=True)


class DescriptionResolver(Generic[DescriptionT], Protocol):
    def __call__(self, module_paths: Iterable[Path]) -> Sequence[DescriptionT]:
        """
        Resolve the provided module_paths to their corresponding DescriptionT.

        Args:
            module_paths (Iterable[Path]):
                The paths to the modules to load.

        Returns:
            Sequence[DescriptionT]: The loaded descriptions.
        """


class DefaultDescriptionResolver(Generic[DescriptionT]):
    """
    DefaultDescriptionResolver provides a default implementation for retrieving the
    DescriptionT.
    """

    def __init__(
        self,
        description_variable="description",
        external_namespace="sbe.eggstensibility.external",
    ):
        """
        Create a new DefaultDescriptionResolver with the given description_variable

        Args:
            description_variable (str):
                The name of the variable in the module containing the extension description.
            external_namespace (str):
                The namespace under which to place the loaded modules.
        """
        self._description_variable = description_variable
        self._external_namespace = external_namespace

    def _initialize_extension_points(self) -> None:
        namespace_components = self._external_namespace.split(".")

        for i in range(len(namespace_components)):
            module_namespace = ".".join(namespace_components[: (i + 1)])
            sys.modules.setdefault(module_namespace, types.ModuleType(module_namespace))

    def _initialize_module(self, name: str, path: Path):
        namespace = f"{self._external_namespace}.{name}"

        if namespace in sys.modules:
            return sys.modules[namespace]

        spec = importlib.util.spec_from_file_location(namespace, path)

        if spec is None or spec.loader is None:
            return None

        module = importlib.util.module_from_spec(spec)
        if module is None:
            return None

        spec.loader.exec_module(module)
        sys.modules[namespace] = module
        return module

    def _initialize_extension_directory(
        self, module_path: Path, module_directory_init: Path
    ):
        module_parent_name = module_directory_init.parent.stem
        parent_module = self._initialize_module(
            module_parent_name, module_directory_init
        )

        module_name = f"{module_parent_name}.{module_path.stem}"

        if parent_module is not None:
            return self._initialize_module(module_name, module_path)
        else:
            return None

    def _initialize_extension_standalone(self, module_path: Path):
        return self._initialize_module(module_path.name, module_path)

    def _initialize_extension_module(self, module_path: Path):
        if (module_directory_init := module_path.parent / "__init__.py").is_file():
            return self._initialize_extension_directory(
                module_path, module_directory_init
            )
        else:
            return self._initialize_extension_standalone(module_path)

    def _load_description(self, module_path: Path) -> Optional[DescriptionT]:
        module = self._initialize_extension_module(module_path)
        if module is None:
            return None
        return getattr(module, self._description_variable, None)

    def _load_descriptions(
        self, module_paths: Iterable[Path]
    ) -> Iterable[DescriptionT]:
        return (
            desc
            for mp in module_paths
            if (desc := self._load_description(mp)) is not None
        )

    def __call__(self, module_paths: Iterable[Path]) -> Sequence[DescriptionT]:
        """
        Resolve the provided module_paths to their corresponding DescriptionT.

        Args:
            module_paths (Iterable[Path]):
                The paths to the modules to load.

        Returns:
            Sequence[DescriptionT]: The loaded descriptions.
        """
        self._initialize_extension_points()
        return list(self._load_descriptions(module_paths))
