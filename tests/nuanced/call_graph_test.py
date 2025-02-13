from deepdiff import DeepDiff
import inspect
import pytest
from nuanced.lib.call_graph import CallGraph
from tests.fixtures.fixture_class import FixtureClass
from tests.fixtures.other_fixture_class import OtherFixtureClass

def test_init_with_defaults() -> None:
    entry_points = [inspect.getfile(FixtureClass)]

    call_graph = CallGraph(entry_points)

    assert call_graph.call_graph.entry_points == entry_points

def test_to_dict() -> None:
    expected = {'tests.fixtures.fixture_class': ['tests.fixtures.fixture_class.FixtureClass'], 'tests.fixtures.fixture_class.FixtureClass': [], 'tests.fixtures.other_fixture_class': ['tests.fixtures.other_fixture_class.OtherFixtureClass'], 'tests.fixtures.other_fixture_class.OtherFixtureClass': [], 'tests.fixtures.other_fixture_class.OtherFixtureClass.baz': ['tests.fixtures.fixture_class.FixtureClass.bar', 'tests.fixtures.fixture_class.FixtureClass.__init__'], 'tests.fixtures.fixture_class.FixtureClass.__init__': [], 'tests.fixtures.fixture_class.FixtureClass.bar': ['tests.fixtures.fixture_class.FixtureClass.foo'], 'tests.fixtures.fixture_class.FixtureClass.foo': []}
    entry_points = [
       inspect.getfile(FixtureClass),
       inspect.getfile(OtherFixtureClass),
    ]
    call_graph = CallGraph(entry_points)
    call_graph.generate()

    call_graph_dict = call_graph.to_dict()

    diff = DeepDiff(call_graph_dict, expected)
    assert diff == {}
