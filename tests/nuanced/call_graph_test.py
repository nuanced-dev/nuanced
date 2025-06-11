from deepdiff import DeepDiff
import inspect
import os
import pytest
from nuanced.lib import call_graph
from tests.package_fixtures.fixture_class import FixtureClass


def test_generate_with_package_files_returns_call_graph_dict() -> None:
    entry_points = [
        "tests/package_fixtures/scripts/script.py",
        "tests/package_fixtures/__init__.py",
        "tests/package_fixtures/fixture_class.py",
        "tests/package_fixtures/nested_modules/nested_fixture_class.py",
        "tests/package_fixtures/nested_package/__init__.py",
        "tests/package_fixtures/nested_package/mod_one.py",
    ]
    package_path = "tests/package_fixtures"
    expected = {
        "package_fixtures.nested_modules.nested_fixture_class": {
          "filepath": os.path.abspath("tests/package_fixtures/nested_modules/nested_fixture_class.py"),
          "callees": [
            "package_fixtures.nested_modules.nested_fixture_class.NestedFixtureClass"
          ],
          "lineno": 1,
          "end_lineno": 3
        },
        "package_fixtures.nested_modules.nested_fixture_class.NestedFixtureClass.hello_world": {
          "filepath": os.path.abspath("tests/package_fixtures/nested_modules/nested_fixture_class.py"),
          "callees": [],
          "lineno": 2,
          "end_lineno": 3
        },
        "package_fixtures.scripts.script": {
          "filepath": os.path.abspath("tests/package_fixtures/scripts/script.py"),
          "callees": [
            "package_fixtures.fixture_class",
            "package_fixtures.scripts.script.run"
          ],
          "lineno": 1,
          "end_lineno": 9
        },
        "package_fixtures.scripts.script.run": {
          "filepath": os.path.abspath("tests/package_fixtures/scripts/script.py"),
          "callees": [
            "package_fixtures.fixture_class.helper_function",
            "package_fixtures.fixture_class.FixtureClass.bar",
            "package_fixtures.fixture_class.FixtureClass.__init__"
          ],
          "lineno": 4,
          "end_lineno": 7
        },
        "package_fixtures.fixture_class": {
          "filepath": os.path.abspath("tests/package_fixtures/fixture_class.py"),
          "callees": [
            "package_fixtures.nested_modules.nested_fixture_class",
            "package_fixtures.fixture_class.FixtureClass",
            "package_fixtures.nested_package.mod_one",
          ],
          "lineno": 1,
          "end_lineno": 20
        },
        "package_fixtures.fixture_class.helper_function": {
          "filepath": os.path.abspath("tests/package_fixtures/fixture_class.py"),
          "callees": [
            "package_fixtures.nested_modules.nested_fixture_class.NestedFixtureClass.hello_world"
          ],
          "lineno": 6,
          "end_lineno": 9
        },
        "package_fixtures.fixture_class.FixtureClass.__init__": {
          "filepath": os.path.abspath("tests/package_fixtures/fixture_class.py"),
          "callees": [],
          "lineno": 12,
          "end_lineno": 13
        },
        "package_fixtures.fixture_class.FixtureClass.foo": {
          "filepath": os.path.abspath("tests/package_fixtures/fixture_class.py"),
          "callees": [
            "datetime.datetime.now",
            "package_fixtures.nested_package.mod_one.nested_package_mod_one_fn_one",
          ],
          "lineno": 15,
          "end_lineno": 17
        },
        "package_fixtures.fixture_class.FixtureClass.bar": {
          "filepath": os.path.abspath("tests/package_fixtures/fixture_class.py"),
          "callees": [
            "package_fixtures.fixture_class.FixtureClass.foo"
          ],
          "lineno": 19,
          "end_lineno": 20
        },
        "package_fixtures": {
          "filepath": os.path.abspath("tests/package_fixtures/__init__.py"),
          "callees": [],
          "lineno": 0,
          "end_lineno": 0
        },
        "package_fixtures.nested_package": {
          "filepath": os.path.abspath("tests/package_fixtures/nested_package/__init__.py"),
          "callees": [],
          "lineno": 0,
          "end_lineno": 0
        },
        "package_fixtures.nested_package.mod_one": {
          "filepath": os.path.abspath("tests/package_fixtures/nested_package/mod_one.py"),
          "callees": [],
          "lineno": 1,
          "end_lineno": 2
        },
        "package_fixtures.nested_package.mod_one.nested_package_mod_one_fn_one": {
          "filepath": os.path.abspath("tests/package_fixtures/nested_package/mod_one.py"),
          "callees": [],
          "lineno": 1,
          "end_lineno": 2
        }
      }

    call_graph_dict = call_graph.generate(entry_points, package_path=package_path)

    diff = DeepDiff(call_graph_dict, expected, ignore_order=True)
    assert diff == {}

def test_generate_with_module_files_returns_call_graph_dict() -> None:
    entry_points = [
        "tests/module_fixtures/module_one.py",
        "tests/module_fixtures/module_two.py",
    ]
    expected = {
        "module_fixtures.module_one": {
          "filepath": os.path.abspath("tests/module_fixtures/module_one.py"),
          "callees": ["module_fixtures.module_two"],
          "lineno": 1,
          "end_lineno": 8
        },
        "module_fixtures.module_one.mod_one_fn_one": {
          "filepath": os.path.abspath("tests/module_fixtures/module_one.py"),
          "callees": [
            "tests.package_fixtures.fixture_class.FixtureClass",
            "module_fixtures.module_two.mod_two_fn_one"
          ],
          "lineno": 4,
          "end_lineno": 8
        },
        "module_fixtures.module_two": {
          "filepath": os.path.abspath("tests/module_fixtures/module_two.py"),
          "callees": [],
          "lineno": 1,
          "end_lineno": 2
        },
        "module_fixtures.module_two.mod_two_fn_one": {
          "filepath": os.path.abspath("tests/module_fixtures/module_two.py"),
          "callees": [],
          "lineno": 1,
          "end_lineno": 2
        },
    }

    call_graph_dict = call_graph.generate(entry_points, package_path="tests/module_fixtures")

    diff = DeepDiff(call_graph_dict, expected, ignore_order=True)
    assert diff == {}

def test_generate_defaults_with_packages_and_modules_returns_call_graph_dict() -> None:
    entry_points = [
        'tests/package_fixtures/fixture_class.py',
        'tests/package_fixtures/__init__.py',
        'tests/package_fixtures/scripts/script.py',
        'tests/package_fixtures/nested_package/__init__.py',
        'tests/package_fixtures/nested_package/mod_one.py',
        'tests/package_fixtures/nested_modules/nested_fixture_class.py',
        'tests/module_fixtures/module_one.py',
        'tests/module_fixtures/module_two.py',
    ]
    expected = {
        "tests.package_fixtures.nested_modules.nested_fixture_class": {
           "filepath": os.path.abspath("tests/package_fixtures/nested_modules/nested_fixture_class.py"),
           "callees": [
             "tests.package_fixtures.nested_modules.nested_fixture_class.NestedFixtureClass"
           ],
           "lineno": 1,
           "end_lineno": 3
        },
        "tests.package_fixtures.nested_modules.nested_fixture_class.NestedFixtureClass.hello_world": {
          "filepath": os.path.abspath("tests/package_fixtures/nested_modules/nested_fixture_class.py"),
          "callees": [],
          "lineno": 2,
          "end_lineno": 3
        },
        "tests.package_fixtures.scripts.script": {
          "filepath": os.path.abspath("tests/package_fixtures/scripts/script.py"),
          "callees": [
            "tests.package_fixtures.scripts.script.run"
          ],
          "lineno": 1,
          "end_lineno": 9
        },
        "tests.package_fixtures.scripts.script.run": {
          "filepath": os.path.abspath("tests/package_fixtures/scripts/script.py"),
          "callees": [
            "tests.package_fixtures.fixture_class.helper_function",
            "fixture_class.FixtureClass"
          ],
          "lineno": 4,
          "end_lineno": 7
        },
        "tests.module_fixtures.module_one": {
          "filepath": os.path.abspath("tests/module_fixtures/module_one.py"),
          "callees": [],
          "lineno": 1,
          "end_lineno": 8
        },
        "tests.module_fixtures.module_one.mod_one_fn_one": {
          "filepath": os.path.abspath("tests/module_fixtures/module_one.py"),
          "callees": [
            "tests.package_fixtures.fixture_class.FixtureClass.foo",
            "module_two.mod_two_fn_one",
            "tests.package_fixtures.fixture_class.FixtureClass.__init__"
          ],
          "lineno": 4,
          "end_lineno": 8
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
        },
        "tests.package_fixtures": {
          "filepath": os.path.abspath("tests/package_fixtures/__init__.py"),
          "callees": [],
          "lineno": 0,
          "end_lineno": 0
        },
        "tests.package_fixtures.fixture_class": {
          "filepath": os.path.abspath("tests/package_fixtures/fixture_class.py"),
          "callees": [
            "tests.package_fixtures.fixture_class.FixtureClass"
          ],
          "lineno": 1,
          "end_lineno": 20
        },
        "tests.package_fixtures.fixture_class.helper_function": {
          "filepath": os.path.abspath("tests/package_fixtures/fixture_class.py"),
          "callees": [
            "nested_modules.nested_fixture_class.NestedFixtureClass"
          ],
          "lineno": 6,
          "end_lineno": 9
        },
        "tests.package_fixtures.fixture_class.FixtureClass.__init__": {
          "filepath": os.path.abspath("tests/package_fixtures/fixture_class.py"),
          "callees": [],
          "lineno": 12,
          "end_lineno": 13
        },
        "tests.package_fixtures.fixture_class.FixtureClass.foo": {
          "filepath": os.path.abspath("tests/package_fixtures/fixture_class.py"),
          "callees": [
            "datetime.datetime.now",
            "tests.package_fixtures.nested_package.mod_one.nested_package_mod_one_fn_one",
          ],
          "lineno": 15,
          "end_lineno": 17
        },
        "tests.package_fixtures.fixture_class.FixtureClass.bar": {
          "filepath": os.path.abspath("tests/package_fixtures/fixture_class.py"),
          "callees": [
            "tests.package_fixtures.fixture_class.FixtureClass.foo"
          ],
          "lineno": 19,
          "end_lineno": 20
        },
        "tests.package_fixtures.nested_package": {
          "filepath": os.path.abspath("tests/package_fixtures/nested_package/__init__.py"),
          "callees": [],
          "lineno": 0,
          "end_lineno": 0
        },
        "tests.package_fixtures.nested_package.mod_one": {
          "filepath": os.path.abspath("tests/package_fixtures/nested_package/mod_one.py"),
          "callees": [],
          "lineno": 1,
          "end_lineno": 2
        },
        "tests.package_fixtures.nested_package.mod_one.nested_package_mod_one_fn_one": {
          "filepath": os.path.abspath("tests/package_fixtures/nested_package/mod_one.py"),
          "callees": [],
          "lineno": 1,
          "end_lineno": 2
        }
    }

    call_graph_dict = call_graph.generate(entry_points)

    diff = DeepDiff(expected, call_graph_dict, ignore_order=True)
    assert diff == {}

def test_generate_with_packages_and_modules_returns_call_graph_dict() -> None:
    entry_points = [
        "tests/package_fixtures/fixture_class.py",
        "tests/package_fixtures/__init__.py",
        "tests/package_fixtures/scripts/script.py",
        "tests/package_fixtures/nested_modules/nested_fixture_class.py",
        "tests/module_fixtures/module_one.py",
        "tests/module_fixtures/module_two.py",
        "tests/package_fixtures/nested_package/__init__.py",
        "tests/package_fixtures/nested_package/mod_one.py"
    ]
    package_path = "tests/package_fixtures"
    expected = {
        "package_fixtures.nested_modules.nested_fixture_class": {
          "filepath": os.path.abspath("tests/package_fixtures/nested_modules/nested_fixture_class.py"),
          "callees": [
            "package_fixtures.nested_modules.nested_fixture_class.NestedFixtureClass"
          ],
          "lineno": 1,
          "end_lineno": 3
        },
        "package_fixtures.nested_modules.nested_fixture_class.NestedFixtureClass.hello_world": {
          "filepath": os.path.abspath("tests/package_fixtures/nested_modules/nested_fixture_class.py"),
          "callees": [],
          "lineno": 2,
          "end_lineno": 3
        },
        "package_fixtures.scripts.script": {
          "filepath": os.path.abspath("tests/package_fixtures/scripts/script.py"),
          "callees": [
            "package_fixtures.fixture_class",
            "package_fixtures.scripts.script.run"
          ],
          "lineno": 1,
          "end_lineno": 9
        },
        "package_fixtures.scripts.script.run": {
          "filepath": os.path.abspath("tests/package_fixtures/scripts/script.py"),
          "callees": [
            "package_fixtures.fixture_class.FixtureClass.bar",
            "package_fixtures.fixture_class.helper_function",
            "package_fixtures.fixture_class.FixtureClass.__init__"
          ],
          "lineno": 4,
          "end_lineno": 7
        },
        "package_fixtures.fixture_class": {
          "filepath": os.path.abspath("tests/package_fixtures/fixture_class.py"),
          "callees": [
            "package_fixtures.nested_modules.nested_fixture_class",
            "package_fixtures.nested_package.mod_one",
            "package_fixtures.fixture_class.FixtureClass"
          ],
          "lineno": 1,
          "end_lineno": 20
        },
        "package_fixtures.fixture_class.helper_function": {
          "filepath": os.path.abspath("tests/package_fixtures/fixture_class.py"),
          "callees": [
            "package_fixtures.nested_modules.nested_fixture_class.NestedFixtureClass.hello_world"
          ],
          "lineno": 6,
          "end_lineno": 9
        },
        "package_fixtures.fixture_class.FixtureClass.__init__": {
          "filepath": os.path.abspath("tests/package_fixtures/fixture_class.py"),
          "callees": [],
          "lineno": 12,
          "end_lineno": 13
        },
        "package_fixtures.fixture_class.FixtureClass.foo": {
          "filepath": os.path.abspath("tests/package_fixtures/fixture_class.py"),
          "callees": [
            "datetime.datetime.now",
            "package_fixtures.nested_package.mod_one.nested_package_mod_one_fn_one",
          ],
          "lineno": 15,
          "end_lineno": 17
        },
        "package_fixtures.fixture_class.FixtureClass.bar": {
          "filepath": os.path.abspath("tests/package_fixtures/fixture_class.py"),
          "callees": [
            "package_fixtures.fixture_class.FixtureClass.foo"
          ],
          "lineno": 19,
          "end_lineno": 20
        },
        "module_fixtures.module_one": {
          "filepath": os.path.abspath("tests/module_fixtures/module_one.py"),
          "callees": [
            "package_fixtures.fixture_class",
            "module_fixtures.module_two"
          ],
          "lineno": 1,
          "end_lineno": 8
        },
        "module_fixtures.module_one.mod_one_fn_one": {
          "filepath": os.path.abspath("tests/module_fixtures/module_one.py"),
          "callees": [
            "module_fixtures.module_two.mod_two_fn_one",
            "module_two.mod_two_fn_one",
            "package_fixtures.fixture_class.FixtureClass.foo",
            "package_fixtures.fixture_class.FixtureClass.__init__"
          ],
          "lineno": 4,
          "end_lineno": 8
        },
        "module_fixtures.module_two": {
          "filepath": os.path.abspath("tests/module_fixtures/module_two.py"),
          "callees": [],
          "lineno": 1,
          "end_lineno": 2
        },
        "module_fixtures.module_two.mod_two_fn_one": {
          "filepath": os.path.abspath("tests/module_fixtures/module_two.py"),
          "callees": [],
          "lineno": 1,
          "end_lineno": 2
        },
        "package_fixtures": {
          "filepath": os.path.abspath("tests/package_fixtures/__init__.py"),
          "callees": [],
          "lineno": 0,
          "end_lineno": 0
        },
        "package_fixtures.nested_package": {
          "filepath": os.path.abspath("tests/package_fixtures/nested_package/__init__.py"),
          "callees": [],
          "lineno": 0,
          "end_lineno": 0
        },
        "package_fixtures.nested_package.mod_one": {
          "filepath": os.path.abspath("tests/package_fixtures/nested_package/mod_one.py"),
          "callees": [],
          "lineno": 1,
          "end_lineno": 2
        },
        "package_fixtures.nested_package.mod_one.nested_package_mod_one_fn_one": {
          "filepath": os.path.abspath("tests/package_fixtures/nested_package/mod_one.py"),
          "callees": [],
          "lineno": 1,
          "end_lineno": 2
        }
    }

    call_graph_dict = call_graph.generate(entry_points, package_path=package_path)

    diff = DeepDiff(expected, call_graph_dict, ignore_order=True)
    assert diff == {}
