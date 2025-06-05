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
            "callees": ["tests.fixtures.fixture_class.FixtureClass"],
            "lineno": 1,
            "end_lineno": 11,
        },
        "tests.fixtures.fixture_class.FixtureClass.__init__": {
            "filepath": os.path.abspath("tests/fixtures/fixture_class.py"),
            "callees": [],
            "lineno": 4,
            "end_lineno": 5,
        },
        "tests.fixtures.fixture_class.FixtureClass.foo": {
            "filepath": os.path.abspath("tests/fixtures/fixture_class.py"),
            "callees": ["datetime.datetime.tzinfo"],
            "lineno": 7,
            "end_lineno": 8,
        },
        "tests.fixtures.fixture_class.FixtureClass.bar": {
            "filepath": os.path.abspath("tests/fixtures/fixture_class.py"),
            "callees": ["tests.fixtures.fixture_class.FixtureClass.foo"],
            "lineno": 10,
            "end_lineno": 11,
        }
    }

    call_graph_dict = call_graph.generate(entry_points)

    diff = DeepDiff(call_graph_dict, expected)

    assert diff == {}

def test_generate_with_package_returns_call_graph_dict() -> None:
    entry_points = [inspect.getfile(FixtureClass)]
    expected = {
        "fixtures.fixture_class": {
            "filepath": os.path.abspath("tests/fixtures/fixture_class.py"),
            "callees": ["fixtures.fixture_class.FixtureClass"],
            "lineno": 1,
            "end_lineno": 11,
        },
        "fixtures.fixture_class.FixtureClass.__init__": {
            "filepath": os.path.abspath("tests/fixtures/fixture_class.py"),
            "callees": [],
            "lineno": 4,
            "end_lineno": 5,
        },
        "fixtures.fixture_class.FixtureClass.foo": {
            "filepath": os.path.abspath("tests/fixtures/fixture_class.py"),
            "callees": ["datetime.datetime.tzinfo"],
            "lineno": 7,
            "end_lineno": 8,
        },
        "fixtures.fixture_class.FixtureClass.bar": {
            "filepath": os.path.abspath("tests/fixtures/fixture_class.py"),
            "callees": ["fixtures.fixture_class.FixtureClass.foo"],
            "lineno": 10,
            "end_lineno": 11,
        }
    }

    call_graph_dict = call_graph.generate(entry_points, package_path="tests/fixtures")

    diff = DeepDiff(call_graph_dict, expected)

    assert diff == {}
