import concurrent
import os
import pytest
from nuanced import CodeGraph
from nuanced.lib.call_graph import CallGraph

def test_init_with_valid_path(mocker) -> None:
    mocker.patch("os.mkdir", lambda _dirname, exist_ok=False: None)
    mock_file = mocker.mock_open()
    mocker.patch("builtins.open", mock_file)
    path = "tests/fixtures"
    spy = mocker.spy(CallGraph, "__init__")
    expected_filepaths = [
        os.path.abspath("tests/fixtures/fixture_class.py"),
    ]

    CodeGraph.init(path)

    filepaths = spy.call_args.args[1]
    assert len(filepaths) == len(expected_filepaths)
    for p in filepaths:
        assert p in expected_filepaths

def test_init_with_invalid_path_returns_errors(mocker) -> None:
    invalid_path = "foo"

    code_graph_result = CodeGraph.init(invalid_path)

    assert len(code_graph_result.errors) == 1
    assert type(code_graph_result.errors[0]) == FileNotFoundError

def test_init_with_no_eligible_files_returns_errors(mocker) -> None:
    no_eligible_files_path = "tests/fixtures/ineligible"

    code_graph_result = CodeGraph.init(no_eligible_files_path)

    assert len(code_graph_result.errors) == 1
    assert str(code_graph_result.errors[0]) == f"No eligible files found in {os.path.abspath(no_eligible_files_path)}"

def test_init_with_valid_path_persists_code_graph(mocker) -> None:
    mocker.patch("os.mkdir", lambda _dirname, exist_ok=False: None)
    os_spy = mocker.spy(os, "mkdir")
    mock_file = mocker.mock_open()
    mocker.patch("builtins.open", mock_file)
    expected_path = os.path.abspath(f"tests/fixtures/{CodeGraph.NUANCED_DIRNAME}")

    CodeGraph.init("tests/fixtures")

    received_dir_path = os_spy.call_args.args[0]
    assert received_dir_path == expected_path
    mock_file.assert_called_with(f'{expected_path}/{CodeGraph.NUANCED_GRAPH_FILENAME}', "w+")

def test_init_with_valid_path_returns_code_graph(mocker) -> None:
    mocker.patch("os.mkdir", lambda _dirname, exist_ok=False: None)
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

def test_init_timeout_returns_errors(mocker) -> None:
    path = "tests/fixtures"
    mocker.patch("nuanced.CodeGraph.INIT_TIMEOUT_SECONDS", 0)

    code_graph_result = CodeGraph.init(path)
    errors = code_graph_result.errors

    assert len(errors) == 1
    assert type(errors[0]) == concurrent.futures.TimeoutError
