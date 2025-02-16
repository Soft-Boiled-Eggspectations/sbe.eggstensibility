from sbe.eggstensibility.defaults import Description


def ctor():
    from ._extension_impl import Extension_ModuleA
    return Extension_ModuleA()


description = Description(
    __name__,   # name of the extension module
    ctor,       # the constructor method
)
