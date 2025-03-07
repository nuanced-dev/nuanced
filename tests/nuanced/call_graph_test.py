from deepdiff import DeepDiff
import inspect
import os
import pytest
from nuanced.lib import call_graph
from tests.fixtures.fixture_class import FixtureClass

def test_generate_with_defaults_returns_call_graph_dict() -> None:
    entry_points = [inspect.getfile(FixtureClass)]
    expected = {
        "tests.fixtures.fixture_class": {
            "filepath": os.path.abspath("tests/fixtures/fixture_class.py"),
            "callees": ["tests.fixtures.fixture_class.FixtureClass"]
        },
        "tests.fixtures.fixture_class.FixtureClass.__init__": {
            "filepath": os.path.abspath("tests/fixtures/fixture_class.py"),
            "callees": []
        },
        "tests.fixtures.fixture_class.FixtureClass.foo": {
            "filepath": os.path.abspath("tests/fixtures/fixture_class.py"),
            "callees": []
        },
        "tests.fixtures.fixture_class.FixtureClass.bar": {
            "filepath": os.path.abspath("tests/fixtures/fixture_class.py"),
            "callees": ["tests.fixtures.fixture_class.FixtureClass.foo"]
        }
    }

    call_graph_dict = call_graph.generate(entry_points)
    diff = DeepDiff(call_graph_dict, expected)

    assert diff == {}
