"""
default provides the `resolve_descriptions` function which resolves a set of dependency
modules, which are loaded with the default implementation of sbe.eggstensibility.

This provides an example implementation to load a set of descriptions which contain
constructors for the specific extension points.

The validation occurs in `test_default.py` located in the parent directory of this 
directory.
"""
from pathlib import Path

from sbe import eggstensibility
from sbe.eggstensibility import defaults

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
        .add_module_resolver(defaults.DirectoryModuleResolver("extension.py"))
        .add_description_resolver(defaults.DescriptionResolver("description", "sbe.eggstensibility.external"))
        .configure_identifier_resolver(defaults.ResolveIdentifier())
        .configure_dependency_resolver(defaults.ResolveDependency())
        .add_harvest_path(*paths)
        .build()
        .load_extension_descriptions()
    )
    