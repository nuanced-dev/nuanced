from deepdiff import DeepDiff
import inspect
import os
import pytest
from nuanced.lib import call_graph
from tests.package_fixtures.fixture_class import FixtureClass

def test_generate_with_top_level_package_sets_correct_scope_prefix() -> None:
    entry_points = ["tests/__init__.py"]

    call_graph_dict = call_graph.generate(entry_points)

    assert "tests" in call_graph_dict

def test_generate_with_nested_package_returns_call_graph_dict() -> None:
    entry_points = [
        "tests/package_fixtures/nested_package/__init__.py",
        "tests/package_fixtures/nested_package/mod_one.py",
    ]
    expected_edges = {
        "tests.package_fixtures.nested_package": [],
        "tests.package_fixtures.nested_package.mod_one": [],
        "tests.package_fixtures.nested_package.mod_one.nested_package_mod_one_fn_one": [
            "tests.module_fixtures.module_two.mod_two_fn_one"
        ],
    }

    call_graph_dict = call_graph.generate(entry_points)

    for caller, callees in expected_edges.items():
        assert call_graph_dict[caller]["callees"] == callees

def test_generate_with_nested_module_returns_call_graph_dict() -> None:
    entry_points = ["tests/module_fixtures/nested/nested_mod.py"]
    expected_edges = {
      "tests.module_fixtures.module_two": [],
      "tests.module_fixtures.module_two.mod_two_fn_one": [],
      "tests.module_fixtures.nested.nested_mod": ["tests.module_fixtures.module_two"],
      "tests.module_fixtures.nested.nested_mod.nested_mod_fn_one": [
          "tests.module_fixtures.module_two.mod_two_fn_one"
      ],
    }

    call_graph_dict = call_graph.generate(entry_points)

    for caller, callees in expected_edges.items():
        assert call_graph_dict[caller]["callees"] == callees

def test_generate_with_package_files_returns_call_graph_dict() -> None:
    entry_points = [
        "tests/package_fixtures/scripts/script.py",
        "tests/package_fixtures/__init__.py",
        "tests/package_fixtures/fixture_class.py",
        "tests/package_fixtures/nested_modules/nested_fixture_class.py",
        "tests/package_fixtures/nested_package/__init__.py",
        "tests/package_fixtures/nested_package/mod_one.py",
    ]
    expected_edges = {
        "tests.package_fixtures.nested_modules.nested_fixture_class": [
            "tests.package_fixtures.nested_modules.nested_fixture_class.NestedFixtureClass"
        ],
        "tests.package_fixtures.nested_modules.nested_fixture_class.NestedFixtureClass.hello_world": [],
        "tests.package_fixtures.scripts.script": [
            "tests.package_fixtures.fixture_class",
            "tests.package_fixtures.scripts.script.run"
        ],
        "tests.package_fixtures.scripts.script.run": [
            "tests.package_fixtures.fixture_class.helper_function",
            "tests.package_fixtures.fixture_class.FixtureClass.bar",
            "tests.package_fixtures.fixture_class.FixtureClass.__init__"
        ],
        "tests.package_fixtures.fixture_class": [
            "tests.package_fixtures.nested_modules.nested_fixture_class",
            "tests.package_fixtures.fixture_class.FixtureClass",
            "tests.package_fixtures.nested_package.mod_one",
        ],
        "tests.package_fixtures.fixture_class.helper_function": [
            "tests.package_fixtures.nested_modules.nested_fixture_class.NestedFixtureClass.hello_world"
        ],
        "tests.package_fixtures.fixture_class.FixtureClass.__init__": [],
        "tests.package_fixtures.fixture_class.FixtureClass.foo": [
            "datetime.datetime.now",
            "tests.package_fixtures.nested_package.mod_one.nested_package_mod_one_fn_one",
        ],
        "tests.package_fixtures.fixture_class.FixtureClass.bar": [
            "tests.package_fixtures.fixture_class.FixtureClass.foo"
        ],
        "tests.package_fixtures": [],
        "tests.package_fixtures.nested_package": [],
        "tests.package_fixtures.nested_package.mod_one": [],
        "tests.package_fixtures.nested_package.mod_one.nested_package_mod_one_fn_one": [
            "tests.module_fixtures.module_two.mod_two_fn_one"
        ],
    }

    call_graph_dict = call_graph.generate(entry_points)

    for caller, expected_callees in expected_edges.items():
        callees = call_graph_dict[caller]["callees"]
        diff = DeepDiff(expected_callees, callees, ignore_order=True)
        assert diff == {}

def test_generate_with_module_files_returns_call_graph_dict() -> None:
    entry_points = [
        "tests/module_fixtures/module_one.py",
        "tests/module_fixtures/module_two.py",
    ]
    expected_edges = {
        "tests.module_fixtures.module_one": [
          "tests.package_fixtures.fixture_class",
          "tests.module_fixtures.module_two"
        ],
        "tests.module_fixtures.module_one.mod_one_fn_one": [
          "module_two.mod_two_fn_one",
          "tests.module_fixtures.module_two.mod_two_fn_one",
          "tests.package_fixtures.fixture_class.FixtureClass.foo",
          "tests.package_fixtures.fixture_class.FixtureClass.__init__"
        ],
        "tests.module_fixtures.module_two": [],
        "tests.module_fixtures.module_two.mod_two_fn_one": [],
        "tests.package_fixtures.fixture_class": [
            "tests.package_fixtures.fixture_class.FixtureClass",
            "tests.package_fixtures.nested_package.mod_one"
        ],
        "tests.package_fixtures.fixture_class.helper_function": [],
        "tests.package_fixtures.fixture_class.FixtureClass.__init__": [],
        "tests.package_fixtures.fixture_class.FixtureClass.foo": [
            "tests.package_fixtures.nested_package.mod_one.nested_package_mod_one_fn_one",
            "datetime.datetime.now"
        ],
        "tests.package_fixtures.fixture_class.FixtureClass.bar": [],
        "tests.package_fixtures.nested_package.mod_one": ["tests.module_fixtures.module_two"],
        "tests.package_fixtures.nested_package.mod_one.nested_package_mod_one_fn_one": [
            "tests.module_fixtures.module_two.mod_two_fn_one"
        ],
    }

    call_graph_dict = call_graph.generate(entry_points)

    for caller, expected_callees in expected_edges.items():
        callees = call_graph_dict[caller]["callees"]
        diff = DeepDiff(expected_callees, callees, ignore_order=True)
        assert diff == {}

def test_generate_defaults_with_packages_and_modules_returns_call_graph_dict() -> None:
    entry_points = [
        "tests/package_fixtures/fixture_class.py",
        "tests/package_fixtures/__init__.py",
        "tests/package_fixtures/scripts/script.py",
        "tests/package_fixtures/nested_package/__init__.py",
        "tests/package_fixtures/nested_package/mod_one.py",
        "tests/package_fixtures/nested_modules/nested_fixture_class.py",
        "tests/module_fixtures/module_one.py",
        "tests/module_fixtures/module_two.py",
    ]
    expected_edges = {
        "tests.package_fixtures.nested_modules.nested_fixture_class": [
            "tests.package_fixtures.nested_modules.nested_fixture_class.NestedFixtureClass"
        ],
        "tests.package_fixtures.nested_modules.nested_fixture_class.NestedFixtureClass.hello_world": [],
        "tests.package_fixtures.scripts.script": [
            "tests.package_fixtures.scripts.script.run",
            "tests.package_fixtures.fixture_class"
        ],
        "tests.package_fixtures.scripts.script.run": [
            "tests.package_fixtures.fixture_class.helper_function",
            "tests.package_fixtures.fixture_class.FixtureClass.__init__",
            "tests.package_fixtures.fixture_class.FixtureClass.bar"
        ],
        "tests.module_fixtures.module_one": [
            "tests.module_fixtures.module_two",
            "tests.package_fixtures.fixture_class"
        ],
        "tests.module_fixtures.module_one.mod_one_fn_one": [
            "tests.package_fixtures.fixture_class.FixtureClass.foo",
            "tests.package_fixtures.fixture_class.FixtureClass.__init__",
            "tests.module_fixtures.module_two.mod_two_fn_one",
            "module_two.mod_two_fn_one",
        ],
        "tests.module_fixtures.module_two": [],
        "tests.module_fixtures.module_two.mod_two_fn_one": [],
        "tests.package_fixtures": [],
        "tests.package_fixtures.fixture_class": [
            "tests.package_fixtures.nested_package.mod_one",
            "tests.package_fixtures.fixture_class.FixtureClass",
            "tests.package_fixtures.nested_modules.nested_fixture_class"
        ],
        "tests.package_fixtures.fixture_class.helper_function": [
            "tests.package_fixtures.nested_modules.nested_fixture_class.NestedFixtureClass.hello_world",
        ],
        "tests.package_fixtures.fixture_class.FixtureClass.__init__": [],
        "tests.package_fixtures.fixture_class.FixtureClass.foo": [
            "datetime.datetime.now",
            "tests.package_fixtures.nested_package.mod_one.nested_package_mod_one_fn_one",
        ],
        "tests.package_fixtures.fixture_class.FixtureClass.bar": [
            "tests.package_fixtures.fixture_class.FixtureClass.foo"
        ],
        "tests.package_fixtures.nested_package": [],
        "tests.package_fixtures.nested_package.mod_one": [],
        "tests.package_fixtures.nested_package.mod_one.nested_package_mod_one_fn_one": [
            "tests.module_fixtures.module_two.mod_two_fn_one"
        ],
    }

    call_graph_dict = call_graph.generate(entry_points)

    for caller, expected_callees in expected_edges.items():
        callees = call_graph_dict[caller]["callees"]
        diff = DeepDiff(expected_callees, callees, ignore_order=True)
        assert diff == {}

def test_generate_output_includes_file_path_and_line_numbers() -> None:
    entry_points = [
        "tests/package_fixtures/nested_package/mod_one.py",
    ]
    expected = {
        "tests.package_fixtures.nested_package.mod_one": {
            "filepath": os.path.abspath("tests/package_fixtures/nested_package/mod_one.py"),
            "callees": [
                "tests.module_fixtures.module_two"
            ],
            "lineno": 1,
            "end_lineno": 4
        },
        "tests.package_fixtures.nested_package.mod_one.nested_package_mod_one_fn_one": {
            "filepath": os.path.abspath("tests/package_fixtures/nested_package/mod_one.py"),
            "callees": [
                "tests.module_fixtures.module_two.mod_two_fn_one"
            ],
            "lineno": 3,
            "end_lineno": 4
        },
        "tests.module_fixtures.module_two": {
            "filepath": os.path.abspath("tests/module_fixtures/module_two.py"),
            "callees": [],
            "lineno": 1,
            "end_lineno": 2
        },
        "tests.module_fixtures.module_two.mod_two_fn_one": {
            "filepath": os.path.abspath("tests/module_fixtures/module_two.py"),
            "callees": [],
            "lineno": 1,
            "end_lineno": 2
        }
    }

    call_graph_dict = call_graph.generate(entry_points)

    diff = DeepDiff(expected, call_graph_dict, ignore_order=True)
    assert diff == {}
