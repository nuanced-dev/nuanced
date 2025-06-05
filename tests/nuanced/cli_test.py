from deepdiff import DeepDiff
import json
import os
from typer.testing import CliRunner
from nuanced import CodeGraph, __version__
from nuanced.cli import app
from nuanced.code_graph import CodeGraphResult, EnrichmentResult


runner = CliRunner(mix_stderr=False)


def test_version_displays_installed_version():
    result = runner.invoke(app, ["--version"])

    assert result.stdout == f"nuanced {__version__}\n"

def test_enrich_finds_relevant_graph_in_file_dir(mocker):
    graph = { "foo.bar": { "filepath": os.path.abspath("foo.py"), "callees": [] } }
    code_graph = CodeGraph(graph=graph)
    mocker.patch(
        "nuanced.cli.CodeGraph.load",
        lambda directory: CodeGraphResult(code_graph=code_graph, errors=[]),
    )
    load_spy = mocker.spy(CodeGraph, "load")

    runner.invoke(app, ["enrich", "foo.py", "bar"])

    load_spy.assert_called_with(directory="")

def test_enrich_finds_relevant_graph_in_file_path_parent_dir(mocker):
    file_path = "foo/bar/baz.py"
    file_dir, _ = os.path.split(file_path)
    top_dir = "foo"
    top_dir_contents = (top_dir, [CodeGraph.NUANCED_DIRNAME, "bar"], ["__init__.py"])
    stub_graph = {}
    result_with_errors = CodeGraphResult(code_graph=None, errors=["Graph not found"])
    valid_result = CodeGraphResult(code_graph=CodeGraph(stub_graph), errors=[])
    mocker.patch("os.walk", lambda directory: [top_dir_contents])
    mocker.patch(
        "nuanced.cli.CodeGraph.load",
        lambda directory: result_with_errors if directory == file_dir else valid_result
    )
    expected_calls = [mocker.call(directory=file_dir)]
    load_spy = mocker.spy(CodeGraph, "load")

    runner.invoke(app, ["enrich", file_path, "hello_world"])

    load_spy.assert_has_calls(expected_calls)

def test_enrich_finds_relevant_graph_in_file_path_scope(mocker):
    file_path = "../foo/bar/baz.py"
    file_dir, _ = os.path.split(file_path)
    top_dir = ".."
    top_dir_contents = (top_dir, ["other", "foo"], [])
    file_parent_dir_contents = ("../foo", [CodeGraph.NUANCED_DIRNAME], [])
    other_dir_contents = ("../other", [CodeGraph.NUANCED_DIRNAME], [])
    file_dir_contents = (file_dir, [], [])
    stub_graph = {}
    result_with_errors = CodeGraphResult(code_graph=None, errors=["Graph not found"])
    valid_result = CodeGraphResult(code_graph=CodeGraph(stub_graph), errors=[])
    mocker.patch(
        "nuanced.cli.CodeGraph.load",
        lambda directory: result_with_errors if directory == file_dir else valid_result
    )
    mocked_contents = [
        top_dir_contents,
        file_parent_dir_contents,
        other_dir_contents,
        file_dir_contents
    ]
    mocker.patch("os.walk", lambda directory: mocked_contents)
    load_spy = mocker.spy(CodeGraph, "load")

    runner.invoke(app, ["enrich", file_path, "hello_world"])

    assert mocker.call(directory="../other") not in load_spy.mock_calls

def test_enrich_fails_to_load_graph_errors(mocker):
    error = FileNotFoundError(f"Nuanced Graph not found in {os.path.abspath('./')}")
    errors = [error]
    mocker.patch(
        "nuanced.cli.CodeGraph.load",
        lambda directory: CodeGraphResult(code_graph=None, errors=errors),
    )
    expected_output = str(error)

    result = runner.invoke(app, ["enrich", "foo.py", "bar"])

    assert expected_output in result.stderr
    assert result.exit_code == 1

def test_enrich_fails_to_find_function_errors(mocker, monkeypatch):
    stub_graph = {}
    code_graph = CodeGraph(graph=stub_graph)
    error_result = EnrichmentResult(result=None, errors=[])
    monkeypatch.setattr(
        code_graph,
        "enrich",
        lambda file_path, function_name, include_builtins: error_result
    )
    mocker.patch(
        "nuanced.cli.CodeGraph.load",
        lambda directory: CodeGraphResult(code_graph=code_graph, errors=[]),
    )
    expected_output = f'Function definition for file path "foo.py" and function name "bar" not found'

    result = runner.invoke(app, ["enrich", "foo.py", "bar"])

    assert expected_output in result.stderr
    assert result.exit_code == 1

def test_enrich_fails_to_enrich_function_errors(mocker, monkeypatch):
    stub_graph = {}
    code_graph = CodeGraph(graph=stub_graph)
    error = ValueError("Something went wrong")
    error_result = EnrichmentResult(result=None, errors=[error])
    monkeypatch.setattr(
        code_graph,
        "enrich",
        lambda file_path, function_name, include_builtins: error_result
    )
    mocker.patch(
        "nuanced.cli.CodeGraph.load",
        lambda directory: CodeGraphResult(code_graph=code_graph, errors=[]),
    )
    expected_output = str(error)

    result = runner.invoke(app, ["enrich", "foo.py", "bar"])

    assert expected_output in result.stderr
    assert result.exit_code == 1

def test_enrich_returns_subgraph_success(mocker):
    expected_output = {
        "foo.bar": {
            "filepath": os.path.abspath("foo.py"),
            "callees": ["foo.baz"],
            "lineno": 3,
            "end_lineno": 5,
        },
        "foo.baz": {
            "filepath": os.path.abspath("foo.py"),
            "callees": [],
            "lineno": 7,
            "end_lineno": 9,
        },
    }
    code_graph = CodeGraph(graph=expected_output)
    mocker.patch(
        "nuanced.cli.CodeGraph.load",
        lambda directory: CodeGraphResult(code_graph=code_graph, errors=[]),
    )

    result = runner.invoke(app, ["enrich", "foo.py", "bar"])
    diff = DeepDiff(json.loads(result.stdout), expected_output)

    assert diff == {}
    assert result.exit_code == 0

def test_enrich_supports_include_builtins_option(mocker):
    code_graph = mocker.MagicMock()
    mocker.patch(
        "nuanced.cli.CodeGraph.load",
        lambda directory: CodeGraphResult(code_graph=code_graph, errors=[]),
    )
    mock_file = mocker.mock_open(read_data="")
    mocker.patch("builtins.open", mock_file)
    expected_enrich_args = {
        "file_path": "foo.py",
        "function_name": "bar",
        "include_builtins": True,
    }
    code_graph_spy = mocker.spy(code_graph, "enrich")

    runner.invoke(app, ["enrich", "foo.py", "bar", "--include-builtins"])

    diff = DeepDiff(expected_enrich_args, code_graph_spy.mock_calls[0].kwargs)
    assert diff == {}

def test_enrich_disables_include_builtins_option_by_default(mocker):
    code_graph = mocker.MagicMock()
    mocker.patch(
        "nuanced.cli.CodeGraph.load",
        lambda directory: CodeGraphResult(code_graph=code_graph, errors=[]),
    )
    mock_file = mocker.mock_open(read_data="")
    mocker.patch("builtins.open", mock_file)
    expected_enrich_args = {
        "file_path": "foo.py",
        "function_name": "bar",
        "include_builtins": False,
    }
    code_graph_spy = mocker.spy(code_graph, "enrich")

    runner.invoke(app, ["enrich", "foo.py", "bar"])

    diff = DeepDiff(expected_enrich_args, code_graph_spy.mock_calls[0].kwargs)
    assert diff == {}
