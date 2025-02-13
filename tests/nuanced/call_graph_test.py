import inspect
import pytest
from nuanced.lib.call_graph import CallGraph
from tests.fixtures.fixture_class import FixtureClass

def test_init_with_defaults() -> None:
    entry_points = [inspect.getfile(FixtureClass)]

    call_graph = CallGraph(entry_points)

    assert call_graph.call_graph.entry_points == entry_points
