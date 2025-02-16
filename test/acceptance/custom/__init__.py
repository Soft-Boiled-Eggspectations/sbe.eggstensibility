"""
custom provides the `resolve_descriptions` function which resolves a set of dependency
modules, which are loaded with the custom implementation of provided in `custom_implementation.py`.

The validation occurs in `test_custom.py` located in the parent directory of this 
directory.
"""
from pathlib import Path

from sbe import eggstensibility

from .custom_implementation import (
    ModuleResolver,
    DescriptionResolver,
    ResolveIdentifier,
    ResolveDependency
)

def resolve_descriptions():
    """
    Resolve the descriptions of a set of extensions located in the `modules` directory.
    """
    root_path = Path(__file__).parent
    paths = [
        root_path / "modules" / "module_b",
        root_path / "modules" / "module_a",
    ]

    return (
        eggstensibility.construct_builder()
        .add_module_resolver(ModuleResolver())
        .add_description_resolver(DescriptionResolver())
        .configure_identifier_resolver(ResolveIdentifier())
        .configure_dependency_resolver(ResolveDependency())
        .add_harvest_path(*paths)
        .build()
        .load_extension_descriptions()
    )
    