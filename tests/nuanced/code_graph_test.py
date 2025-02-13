import os
import pytest
from nuanced import CodeGraph
from nuanced.lib.call_graph import CallGraph

def test_init_with_valid_path(mocker) -> None:
    path = "tests/fixtures"
    spy = mocker.spy(CallGraph, "__init__")
    expected_filepaths = [
        os.path.abspath("tests/fixtures/fixture_class.py"),
        os.path.abspath("tests/fixtures/other_fixture_class.py"),
        os.path.abspath("tests/fixtures/foo.py"),
    ]

    CodeGraph.init(path)

    filepaths = spy.call_args.args[1]
    assert len(filepaths) == len(expected_filepaths)
    for p in filepaths:
        assert p in expected_filepaths

def test_init_with_valid_path_returns_code_graph(mocker) -> None:
    path = "tests/fixtures"
    spy = mocker.spy(CallGraph, "__init__")
    expected_filepaths = [os.path.abspath("tests/fixtures/foo.py")]

    code_graph_result = CodeGraph.init(path)
    code_graph = code_graph_result.code_graph
    errors = code_graph_result.errors

    assert errors == []
    assert code_graph
