from deepdiff import DeepDiff
import json
import os
from typer.testing import CliRunner
from nuanced import CodeGraph
from nuanced.cli import app
from nuanced.code_graph import CodeGraphResult


runner = CliRunner()


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

    assert expected_output in result.stdout
    assert result.exit_code == 1

def test_enrich_returns_subgraph_success(mocker):
    expected_output = {
        "foo.bar": {
            "filepath": os.path.abspath("foo.py"),
            "callees": ["foo.baz"]
        },
        "foo.baz": {
            "filepath": os.path.abspath("foo.py"),
            "callees": [],
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
