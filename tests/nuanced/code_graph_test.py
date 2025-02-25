import json
import multiprocessing
import os
import pytest
import nuanced
from nuanced import CodeGraph
from nuanced.lib.call_graph import generate
from nuanced.lib.utils import WithTimeoutResult

def generate_call_graph(target, args, timeout):
    call_graph_dict = target(entry_points=args)
    return WithTimeoutResult(errors=[], value=call_graph_dict)

def timeout_call_graph_generation(target, args, timeout):
    errors = [multiprocessing.TimeoutError("Operation timed out")]
    return WithTimeoutResult(errors=errors, value=None)

def test_init_with_valid_path_generates_graph_with_expected_files(mocker) -> None:
    mocker.patch("os.makedirs", lambda _dirname, exist_ok=True: None)
    mock_file = mocker.mock_open()
    mocker.patch("builtins.open", mock_file)
    mocker.patch("nuanced.code_graph.with_timeout", generate_call_graph)
    call_graph_generate_spy = mocker.spy(nuanced.lib.call_graph, "generate")
    path = "tests/fixtures"
    expected_filepaths = [os.path.abspath("tests/fixtures/fixture_class.py")]

    CodeGraph.init(path)

    call_graph_generate_spy.assert_called_with(entry_points=expected_filepaths)

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
    mocker.patch("nuanced.code_graph.with_timeout", generate_call_graph)
    expected_path = os.path.abspath(f"tests/fixtures/{CodeGraph.NUANCED_DIRNAME}")

    CodeGraph.init("tests/fixtures")

    received_dir_path = os_spy.call_args.args[0]
    assert received_dir_path == expected_path
    mock_file.assert_called_with(f'{expected_path}/{CodeGraph.NUANCED_GRAPH_FILENAME}', "w+")

def test_init_with_valid_path_returns_code_graph(mocker) -> None:
    mocker.patch("os.makedirs", lambda _dirname, exist_ok=True: None)
    mock_file = mocker.mock_open()
    mocker.patch("builtins.open", mock_file)
    mocker.patch("nuanced.code_graph.with_timeout", generate_call_graph)
    path = "tests/fixtures"
    expected_filepaths = [os.path.abspath("tests/fixtures/foo.py")]

    code_graph_result = CodeGraph.init(path)
    code_graph = code_graph_result.code_graph
    errors = code_graph_result.errors

    assert errors == []
    assert code_graph

def test_init_timeout_returns_errors(mocker) -> None:
    path = "tests/fixtures"
    mocker.patch("nuanced.code_graph.with_timeout", timeout_call_graph_generation)

    code_graph_result = CodeGraph.init(path)
    errors = code_graph_result.errors

    assert len(errors) == 1
    assert type(errors[0]) == multiprocessing.TimeoutError

def test_enrich_with_nonexistent_file() -> None:
    graph = json.loads('{ "foo.bar": { "filepath": "foo.py", "callees": [] } }')
    function_name = "bar"
    nonexistent_filepath = "baz.py"
    code_graph = CodeGraph(graph)

    result = code_graph.enrich(file_path=nonexistent_filepath, function_name=function_name)

    assert result.result == None

def test_enrich_with_nonexistent_function_name() -> None:
    graph = json.loads('{ "foo.bar": { "filepath": "foo.py", "callees": [] } }')
    function_name = "baz"
    nonexistent_filepath = "foo.py"
    code_graph = CodeGraph(graph)

    result = code_graph.enrich(file_path=nonexistent_filepath, function_name=function_name)

    assert result.result == None

def test_enrich_with_valid_input_returns_subgraph() -> None:
    filepath1 = os.path.abspath("foo.py")
    filepath2 = os.path.abspath("utils.py")
    graph = { "foo.bar": { "filepath": filepath1, "callees": ["hello.world"] }, "hello.world": { "filepath": "hello.py", "callees": [] }, "utils.util": { "filepath": filepath2, "callees": [] } }
    expected_result = dict()
    expected_result["foo.bar"] = graph["foo.bar"]
    expected_result["hello.world"] = graph["hello.world"]
    code_graph = CodeGraph(graph)

    result = code_graph.enrich(file_path=filepath1, function_name="bar")

    assert result.result == expected_result

def test_enrich_with_valid_function_path_handles_cycles() -> None:
    filepath1 = os.path.abspath("foo.py")
    filepath2 = os.path.abspath("hello.py")
    filepath3 = os.path.abspath("utils.py")
    graph_with_cycle = { "foo.bar": { "filepath": filepath1, "callees": ["hello.world"] }, "hello.world": { "filepath": filepath2, "callees": ["utils.format"] }, "utils.util": { "filepath": "utils.py", "callees": [] }, "utils.format": { "filepath": filepath3, "callees": ["foo.bar"] } }
    expected_result = dict()
    expected_result["foo.bar"] = graph_with_cycle["foo.bar"]
    expected_result["hello.world"] = graph_with_cycle["hello.world"]
    expected_result["utils.format"] = graph_with_cycle["utils.format"]
    code_graph = CodeGraph(graph_with_cycle)

    result = code_graph.enrich(file_path=filepath1, function_name="bar")

    assert result.result == expected_result

def test_enrich_with_valid_function_path_handles_missing_nodes() -> None:
    filepath1 = os.path.abspath("foo.py")
    filepath2 = os.path.abspath("hello.py")
    filepath3 = os.path.abspath("utils.py")
    graph_with_missing_node = { "foo.bar": { "filepath": filepath1, "callees": ["hello.world"] }, "hello.world": { "filepath": filepath2, "callees": ["<builtin>.dict"] }, "utils.util": { "filepath": filepath3, "callees": [] } }
    expected_result = dict()
    expected_result["foo.bar"] = graph_with_missing_node["foo.bar"]
    expected_result["hello.world"] = graph_with_missing_node["hello.world"]
    code_graph = CodeGraph(graph_with_missing_node)

    result = code_graph.enrich(file_path=filepath1, function_name="bar")

    assert result.result == expected_result

def test_enrich_with_valid_function_path_handles_multiple_definitions() -> None:
    filepath1 = os.path.abspath("foo.py")
    filepath2 = os.path.abspath("hello.py")
    graph = { "foo.class.bar": { "filepath": filepath1, "callees": [] }, "foo.other_class.bar": { "filepath": filepath1, "callees": ["hello.world"] }, "hello.world": { "filepath": filepath2, "callees": ["<builtin>.dict"] } }
    function_name = "bar"
    code_graph = CodeGraph(graph)

    result = code_graph.enrich(file_path=filepath1, function_name=function_name)

    assert len(result.errors) == 1
    assert str(result.errors[0]) == f"Multiple definitions for {function_name} found in {filepath1}: foo.class.bar, foo.other_class.bar"
