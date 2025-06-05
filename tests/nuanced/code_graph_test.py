import json
import multiprocessing
import os
import pytest
from pathlib import Path, PosixPath
import nuanced
from nuanced import CodeGraph
from nuanced.lib.call_graph import generate, BUILTIN_FUNCTION_PREFIX
from nuanced.lib.utils import WithTimeoutResult

def generate_call_graph(target, args, kwargs, timeout):
    call_graph_dict = target(args, **kwargs)
    return WithTimeoutResult(errors=[], value=call_graph_dict)

def timeout_call_graph_generation(target, args, kwargs, timeout):
    errors = [multiprocessing.TimeoutError("Operation timed out")]
    return WithTimeoutResult(errors=errors, value=None)

def test_init_with_valid_path_generates_graph_with_expected_files(mocker) -> None:
    mocker.patch("os.makedirs", lambda _dirname, exist_ok=True: None)
    mock_file = mocker.mock_open()
    mocker.patch("builtins.open", mock_file)
    mocker.patch("nuanced.code_graph.with_timeout", generate_call_graph)
    call_graph_generate_spy = mocker.spy(nuanced.lib.call_graph, "generate")
    path = "tests/fixtures"
    expected_package = os.path.abspath(path)
    expected_filepaths = [
        os.path.abspath("tests/fixtures/fixture_class.py"),
        os.path.abspath("tests/fixtures/__init__.py")
    ]

    CodeGraph.init(path)

    call_graph_generate_spy.assert_called_with(
        entry_points=expected_filepaths,
        package_path=expected_package
    )

def test_init_with_no_package_definitions_in_directory_returns_errors(mocker) -> None:
    path = "."
    expected_error_message = f"No package definition found in {os.path.abspath(path)}: `__init__.py` missing"

    code_graph_result = CodeGraph.init(path)

    assert len(code_graph_result.errors) == 1
    assert type(code_graph_result.errors[0]) == ValueError
    assert str(code_graph_result.errors[0]) == expected_error_message

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
    graph = {
        "foo.bar": {
            "filepath": filepath1,
            "callees": ["hello.world"],
            "lineno": 3,
            "end_lineno": 5,
        },
        "hello.world": {
            "filepath": "hello.py",
            "callees": [],
            "lineno": 3,
            "end_lineno": 5,
        },
        "utils.util": {
            "filepath": filepath2,
            "callees": [],
            "lineno": 3,
            "end_lineno": 5,
        },
    }
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
    graph_with_cycle = {
        "foo.bar": {
            "filepath": filepath1,
            "callees": ["hello.world"],
            "lineno": 3,
            "end_lineno": 5,
         },
        "hello.world": {
            "filepath": filepath2,
            "callees": ["utils.format"],
            "lineno": 3,
            "end_lineno": 5,
        },
        "utils.util": {
            "filepath": "utils.py",
            "callees": [],
            "lineno": 3,
            "end_lineno": 5,
        },
        "utils.format": {
            "filepath": filepath3,
            "callees": ["foo.bar"],
            "lineno": 7,
            "end_lineno": 9,
        }
    }
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
    graph_with_missing_node = {
        "foo.bar": {
            "filepath": filepath1,
            "callees": ["hello.world"],
            "lineno": 3,
            "end_lineno": 5,
        },
        "hello.world": {
            "filepath": filepath2,
            "callees": [],
            "lineno": 3,
            "end_lineno": 5,
        },
        "utils.util": {
            "filepath": filepath3,
            "callees": [],
            "lineno": 3,
            "end_lineno": 5,
        },
    }
    expected_result = dict()
    expected_result["foo.bar"] = graph_with_missing_node["foo.bar"]
    expected_result["hello.world"] = graph_with_missing_node["hello.world"]
    code_graph = CodeGraph(graph_with_missing_node)

    result = code_graph.enrich(file_path=filepath1, function_name="bar")

    assert result.result == expected_result

def test_enrich_with_valid_input_excludes_builtins_by_default(mocker) -> None:
    filepath1 = os.path.abspath("foo.py")
    graph = {
        "foo.bar": {
            "filepath": filepath1,
            "callees": [f"{BUILTIN_FUNCTION_PREFIX}.len"],
            "lineno": 3,
            "end_lineno": 5,
        },
    }
    code_graph = CodeGraph(graph)
    expected_result = dict()
    expected_result["foo.bar"] = {
        "filepath": filepath1,
        "callees": [],
        "lineno": 3,
        "end_lineno": 5,
    }

    result = code_graph.enrich(file_path=filepath1, function_name="bar")

    assert result.result["foo.bar"]["callees"] == []

def test_enrich_with_valid_input_includes_builtins(mocker) -> None:
    filepath1 = os.path.abspath("foo.py")
    graph = {
        "foo.bar": {
            "filepath": filepath1,
            "callees": [f"{BUILTIN_FUNCTION_PREFIX}.len"],
            "lineno": 3,
            "end_lineno": 5,
        },
    }
    code_graph = CodeGraph(graph)
    expected_result = dict()
    expected_result["foo.bar"] = {
        "filepath": filepath1,
        "callees": [],
        "lineno": 3,
        "end_lineno": 5,
    }

    result = code_graph.enrich(
        file_path=filepath1,
        function_name="bar",
        include_builtins=True,
    )

    assert result.result["foo.bar"]["callees"] == ["<builtin>.len"]

def test_enrich_with_valid_function_path_handles_multiple_definitions() -> None:
    filepath1 = os.path.abspath("foo.py")
    filepath2 = os.path.abspath("hello.py")
    graph = { "foo.class.bar": { "filepath": filepath1, "callees": [] }, "foo.other_class.bar": { "filepath": filepath1, "callees": ["hello.world"] }, "hello.world": { "filepath": filepath2, "callees": ["<builtin>.dict"] } }
    function_name = "bar"
    code_graph = CodeGraph(graph)

    result = code_graph.enrich(file_path=filepath1, function_name=function_name)

    assert len(result.errors) == 1
    assert str(result.errors[0]) == f"Multiple definitions for {function_name} found in {filepath1}: foo.class.bar, foo.other_class.bar"

def test_load_success(mocker, monkeypatch) -> None:
    mock_file = mocker.mock_open(read_data="{}")
    mocker.patch("builtins.open", mock_file)
    graph_file_paths = [".nuanced/nuanced-graph.json"]
    monkeypatch.setattr(Path, "glob", lambda _x, _y: graph_file_paths)

    result = CodeGraph.load(directory=".")

    assert result.code_graph

def test_load_multiple_files_found_errors(mocker, monkeypatch) -> None:
    directory = "."
    graph_file_paths = [
        PosixPath(".nuanced/nuanced-graph.json"),
        PosixPath("src/.nuanced/nuanced-graph.json"),
    ]
    graph_file_path_strings = [str(fp) for fp in graph_file_paths]
    expected_error_message = f"Multiple Nuanced Graphs found in {os.path.abspath(directory)}: {', '.join(graph_file_path_strings)}"
    mock_file = mocker.mock_open(read_data="{}")
    mocker.patch("builtins.open", mock_file)
    monkeypatch.setattr(Path, "glob", lambda _x, _y: graph_file_paths)

    result = CodeGraph.load(directory=directory)

    assert len(result.errors) == 1
    assert type(result.errors[0]) == ValueError
    assert str(result.errors[0]) == expected_error_message

def test_load_file_not_found_errors(monkeypatch) -> None:
    monkeypatch.setattr(Path, "glob", lambda _x, _y: [])
    result = CodeGraph.load(directory=".")

    assert len(result.errors) == 1
    assert type(result.errors[0]) == FileNotFoundError
    assert str(result.errors[0]) == f"Nuanced Graph not found in {os.path.abspath('.')}"
