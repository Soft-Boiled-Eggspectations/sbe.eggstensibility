"""
test_custom.py provides the acceptance test for an example custom implementation of
sbe.eggstensibility. It validates that the modules are loaded correctly.

The implementation can be found in `custom.__init__.py`
"""
from . import custom


def test_acceptance_custom():
    descriptions = list(custom.resolve_descriptions())

    assert len(descriptions) == 2
    assert descriptions[0].name == "module_b"
    assert descriptions[1].name == "module_a"

    for descr in descriptions:
        descr.initialize()

    assert descriptions[1].execute("potato") == "module_b: module_a: potato"
    assert descriptions[0].execute("potato") == "module_b: potato"
