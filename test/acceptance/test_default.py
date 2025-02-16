"""
test_default.py provides the acceptance test for the default implementation of
sbe.eggstensibility. It validates that the modules are loaded correctly.

The implementation can be found in `default.__init__.py`
"""
from . import default


def test_acceptance_default():
    descriptions = list(default.resolve_descriptions())

    assert len(descriptions) == 2
    assert descriptions[0].name == "sbe.eggstensibility.external.module_a.extension"
    assert descriptions[1].name == "sbe.eggstensibility.external.module_b.extension"

    from sbe.eggstensibility.external import module_a, module_b
    assert module_a
    assert module_b
