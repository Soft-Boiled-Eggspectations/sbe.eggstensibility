"""
custom_implementation provides a custom implementation for each the sbe.eggstensibility
concepts. Rather than the default definition, it defines extensions as json files
which produces an extension that can be executed separately.
"""
from __future__ import annotations

import importlib
import json
import sys
import types

from pathlib import Path
from typing import Iterable, Sequence

BASE_NAMESPACE = "external_modules"


class Description:
    def __init__(
        self,
        name: str,
        exec_module_path: Path,
        exec_method: str,
        dependencies: Iterable[str],
    ) -> None:
        self._name = name
        self._dependencies = list(dependencies)
        self._exec_module_path = exec_module_path 
        self._exec_method = exec_method

        self._initialized_exec_method = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def dependencies(self) -> Iterable[str]:
        return iter(self._dependencies)

    def initialize(self) -> None:
        if self._initialized_exec_method is not None:
            return
        # This could be moved externally depending on the structure of the tool
        self._initialize_extension_base()
        module = self._initialize_module()
        self._initialized_exec_method = getattr(module, self._exec_method)
        
    def _initialize_extension_base(self): 
        sys.modules.setdefault(BASE_NAMESPACE, types.ModuleType(BASE_NAMESPACE))

    def _initialize_module(self):
        namespace = f"{BASE_NAMESPACE}.{self.name}"

        if namespace in sys.modules:
            return sys.modules[namespace]

        spec = importlib.util.spec_from_file_location(namespace, self._exec_module_path)

        if spec is None or spec.loader is None:
            return None

        module = importlib.util.module_from_spec(spec)
        if module is None:
            return None

        spec.loader.exec_module(module)
        sys.modules[namespace] = module
        return module

    def execute(self, msg: str) -> str:
        if self._initialized_exec_method is None:
            raise RuntimeError("Method not loaded")
        return self._initialized_exec_method(msg)

    @classmethod
    def from_json(cls, json_file: Path) -> Description:
        json_file = json_file.resolve()
        base_path = json_file.parent

        with json_file.open('r') as f:
            content = json.load(f)
        
        return Description(
            content["extension_id"],
            base_path / content["entry-point"]["module"],
            content["entry-point"]["exec"],
            content["dependencies"]
        )

class ModuleResolver:
    def __call__(self, path: Path) -> Iterable[Path]:
        json_file = path / "extension.json"

        if json_file.is_file():
            yield json_file

class DescriptionResolver:
    def __call__(self, module_paths: Iterable[Path]) -> Sequence[Description]:
        return [Description.from_json(p) for p in module_paths]
    

class ResolveIdentifier:
    def __call__(self, description: Description) -> str:
        return description.name
    

class ResolveDependency:
    def __call__(self, description: Description) -> Iterable[str]:
        return description.dependencies
