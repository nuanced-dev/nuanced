import os
import pytest
from nuanced import CodeGraph
from nuanced.lib.call_graph import CallGraph

def test_init_with_valid_path(mocker) -> None:
    mocker.patch("os.mkdir", lambda _dirname: None)
    mock_file = mocker.mock_open()
    mocker.patch("builtins.open", mock_file)
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

def test_init_with_valid_path_persists_code_graph(mocker) -> None:
    mocker.patch("os.mkdir", lambda _dirname: None)
    os_spy = mocker.spy(os, "mkdir")
    mock_file = mocker.mock_open()
    mocker.patch("builtins.open", mock_file)
    expected_path = os.path.abspath("tests/fixtures/.nuanced")

    CodeGraph.init("tests/fixtures")

    received_dir_path = os_spy.call_args.args[0]
    assert received_dir_path == expected_path
    mock_file.assert_called_with(f'{expected_path}/nuanced-graph.json', "w+")

def test_init_with_valid_path_returns_code_graph(mocker) -> None:
    mocker.patch("os.mkdir", lambda _dirname: None)
    mock_file = mocker.mock_open()
    mocker.patch("builtins.open", mock_file)
    path = "tests/fixtures"
    spy = mocker.spy(CallGraph, "__init__")
    expected_filepaths = [os.path.abspath("tests/fixtures/foo.py")]

    code_graph_result = CodeGraph.init(path)
    code_graph = code_graph_result.code_graph
    errors = code_graph_result.errors

    assert errors == []
    assert code_graph
