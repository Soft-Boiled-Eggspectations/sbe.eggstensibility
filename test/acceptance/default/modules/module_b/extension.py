from typing import Iterable

from sbe.eggstensibility.defaults import Description, ExtensionID



def ctor():
    from ._extension_impl import Extension_ModuleB

    return Extension_ModuleB()


def dependencies() -> Iterable[ExtensionID]:
    from sbe.eggstensibility.external.module_a import extension
    yield extension.description.extension_id


description = Description(
    __name__,                              # name of the extension module
    ctor,                                  # the constructor method
    dependencies,
)
