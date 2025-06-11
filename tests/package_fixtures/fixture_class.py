from datetime import datetime
from .nested_modules.nested_fixture_class import NestedFixtureClass
from tests.package_fixtures.nested_package.mod_one import nested_package_mod_one_fn_one


def helper_function():
    n = NestedFixtureClass()
    n.hello_world()
    return None

class FixtureClass():
    def __init__(self):
        self.current_time = None

    def foo(self) -> None:
        nested_package_mod_one_fn_one()
        self.current_time = datetime.now()

    def bar(self) -> None:
        self.foo()
