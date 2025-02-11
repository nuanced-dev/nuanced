from tests.fixtures.fixture_class import FixtureClass

class OtherFixtureClass():
    def baz(self) -> None:
        ins = FixtureClass()
        ins.bar()
