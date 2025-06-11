from datetime import datetime
from .nested_modules.nested_fixture_class import NestedFixtureClass


def helper_function():
    n = NestedFixtureClass()
    n.hello_world()
    return None

class FixtureClass():
    def __init__(self):
        self.current_time = None

    def foo(self) -> None:
        self.current_time = datetime.now()

    def bar(self) -> None:
        self.foo()
