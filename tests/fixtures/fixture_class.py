from datetime import datetime

class FixtureClass():
    def __init__(self):
        self.current_time = None

    def foo(self) -> None:
        self.current_time = datetime.now()

    def bar(self) -> None:
        self.foo()
