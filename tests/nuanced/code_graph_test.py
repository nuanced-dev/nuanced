import concurrent
import json
import os
import pytest
from nuanced import CodeGraph
from nuanced.lib.call_graph import CallGraph

def test_init_with_valid_path(mocker) -> None:
    mocker.patch("os.makedirs", lambda _dirname, exist_ok=True: None)
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
    mocker.patch("os.makedirs", lambda _dirname, exist_ok=True: None)
    os_spy = mocker.spy(os, "makedirs")
    mock_file = mocker.mock_open()
    mocker.patch("builtins.open", mock_file)
    expected_path = os.path.abspath(f"tests/fixtures/{CodeGraph.NUANCED_DIRNAME}")

    CodeGraph.init("tests/fixtures")

    received_dir_path = os_spy.call_args.args[0]
    assert received_dir_path == expected_path
    mock_file.assert_called_with(f'{expected_path}/{CodeGraph.NUANCED_GRAPH_FILENAME}', "w+")

def test_init_with_valid_path_returns_code_graph(mocker) -> None:
    mocker.patch("os.makedirs", lambda _dirname, exist_ok=True: None)
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

def test_enrich_with_invalid_function_path() -> None:
    graph = json.loads('{ "foo.bar": { "filepath": "foo.py", "callees": [] } }')
    nonexistent_function_path = "baz"
    code_graph = CodeGraph(graph)

    result = code_graph.enrich(nonexistent_function_path)

    assert result == None

def test_enrich_with_valid_function_path_returns_subgraph() -> None:
    graph = json.loads('{ "foo.bar": { "filepath": "foo.py", "callees": ["hello.world"] }, "hello.world": { "filepath": "hello.py", "callees": [] }, "utils.util": { "filepath": "utils.py", "callees": [] } }')
    expected_result = dict()
    expected_result["foo.bar"] = graph["foo.bar"]
    expected_result["hello.world"] = graph["hello.world"]
    code_graph = CodeGraph(graph)

    result = code_graph.enrich("foo.bar")

    assert result == expected_result

def test_enrich_with_valid_function_path_handles_cycles() -> None:
    graph_with_cycle = json.loads('{ "foo.bar": { "filepath": "foo.py", "callees": ["hello.world"] }, "hello.world": { "filepath": "hello.py", "callees": ["utils.format"] }, "utils.util": { "filepath": "utils.py", "callees": [] }, "utils.format": { "filepath": "utils.py", "callees": ["foo.bar"] } }')
    expected_result = dict()
    expected_result["foo.bar"] = graph_with_cycle["foo.bar"]
    expected_result["hello.world"] = graph_with_cycle["hello.world"]
    expected_result["utils.format"] = graph_with_cycle["utils.format"]
    code_graph = CodeGraph(graph_with_cycle)

    result = code_graph.enrich("foo.bar")

    assert result == expected_result

def test_enrich_with_valid_function_path_handles_missing_nodes() -> None:
    graph_with_missing_node = json.loads('{ "foo.bar": { "filepath": "foo.py", "callees": ["hello.world"] }, "hello.world": { "filepath": "hello.py", "callees": ["<builtin>.dict"] }, "utils.util": { "filepath": "utils.py", "callees": [] } }')
    expected_result = dict()
    expected_result["foo.bar"] = graph_with_missing_node["foo.bar"]
    expected_result["hello.world"] = graph_with_missing_node["hello.world"]
    code_graph = CodeGraph(graph_with_missing_node)

    result = code_graph.enrich("foo.bar")

    assert result == expected_result
