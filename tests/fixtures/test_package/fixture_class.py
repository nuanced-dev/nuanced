from datetime import datetime


class FixtureClass:
    def foo(self) -> None:
        datetime.tzinfo()


def bar():
    f = FixtureClass()
    f.foo()
