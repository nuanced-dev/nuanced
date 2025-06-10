from ..fixture_class import FixtureClass
from tests.package_fixtures.fixture_class import helper_function

def run():
    helper_function()
    ins = FixtureClass()
    ins.bar()

run()
