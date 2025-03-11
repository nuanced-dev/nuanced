from deepdiff import DeepDiff
import json
import os
from typer.testing import CliRunner
from nuanced import CodeGraph
from nuanced.cli import app
from nuanced.code_graph import CodeGraphResult

runner = CliRunner()

def test_enrich_loads_graph_from_working_dir(mocker):
    graph = { "foo.bar": { "filepath": os.path.abspath("foo.py"), "callees": [] } }
    code_graph = CodeGraph(graph=graph)
    mocker.patch(
        "nuanced.cli.CodeGraph.load",
        lambda directory: CodeGraphResult(code_graph=code_graph, errors=[]),
    )
    load_spy = mocker.spy(CodeGraph, "load")

    runner.invoke(app, ["enrich", "foo.py", "bar"])

    load_spy.assert_called_with(directory=".")

def test_enrich_fails_to_load_graph_errors():
    expected_output = f"Nuanced Graph not found in {os.path.abspath('./')}"

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
