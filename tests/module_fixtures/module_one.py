from .module_two import mod_two_fn_one
from tests.package_fixtures.fixture_class import FixtureClass

def mod_one_fn_one():
    ins = FixtureClass()
    ins.foo()
    mod_two_fn_one()
    return None
