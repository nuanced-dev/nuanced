import pytest
from nuanced.lib.utils import grouped_by_package, grouped_by_directory
from deepdiff import DeepDiff

def test_grouped_by_package() -> None:
    file_paths = [
        "tests/package_fixtures/fixture_class.py",
        "tests/package_fixtures/__init__.py",
        "tests/package_fixtures/scripts/script.py",
        "tests/package_fixtures/nested_modules/nested_fixture_class.py",
        "tests/module_fixtures/module_one.py",
        "tests/module_fixtures/module_two.py",
        "tests/package_fixtures/nested_package/__init__.py",
        "tests/package_fixtures/nested_package/mod_one.py",
        "foo/__init__.py",
        "foo/bar.py",
    ]
    expected_packages = {
        "tests/package_fixtures": [
            "tests/package_fixtures/fixture_class.py",
            "tests/package_fixtures/__init__.py",
            "tests/package_fixtures/scripts/script.py",
            "tests/package_fixtures/nested_modules/nested_fixture_class.py",
            "tests/package_fixtures/nested_package/__init__.py",
            "tests/package_fixtures/nested_package/mod_one.py"
        ],
        "foo": ["foo/__init__.py", "foo/bar.py"],
    }

    groups = grouped_by_package(file_paths)

    diff = DeepDiff(expected_packages, groups, ignore_order=True)
    assert diff == {}

def test_grouped_by_directory() -> None:
    file_paths = [
        "tests/package_fixtures/fixture_class.py",
        "tests/package_fixtures/__init__.py",
        "tests/package_fixtures/scripts/script.py",
        "tests/package_fixtures/nested_modules/nested_fixture_class.py",
        "tests/module_fixtures/module_one.py",
        "tests/module_fixtures/module_two.py",
        "tests/package_fixtures/nested_package/__init__.py",
        "tests/package_fixtures/nested_package/mod_one.py"
    ]
    expected = {
        "tests/package_fixtures": [
            "tests/package_fixtures/fixture_class.py",
            "tests/package_fixtures/__init__.py",
        ],
        "tests/package_fixtures/scripts": ["tests/package_fixtures/scripts/script.py"],
        "tests/package_fixtures/nested_modules": ["tests/package_fixtures/nested_modules/nested_fixture_class.py"],
        "tests/package_fixtures/nested_package": [
            "tests/package_fixtures/nested_package/__init__.py",
            "tests/package_fixtures/nested_package/mod_one.py"
        ],
        "tests/module_fixtures": [
            "tests/module_fixtures/module_one.py",
            "tests/module_fixtures/module_two.py",
        ]
    }

    groups = grouped_by_directory(file_paths)

    diff = DeepDiff(expected, groups, ignore_order=True)
    assert diff == {}
