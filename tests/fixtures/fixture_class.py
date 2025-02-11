from datetime import datetime

class FixtureClass():
    def __init__(self):
        self.tzinfo = None

    def foo(self) -> None:
        self.tzinfo = datetime.tzinfo()

    def bar(self) -> None:
        self.foo()
