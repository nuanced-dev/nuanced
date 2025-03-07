from deepdiff import DeepDiff
import json
import os
from typer.testing import CliRunner

from nuanced.cli import app

runner = CliRunner()

def test_enrich_infers_path_to_nuanced_graph_success(mocker):
    mock_file = mocker.mock_open()
    mocker.patch("builtins.open", mock_file)
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
    mocker.patch("json.load", lambda _x: expected_output)

    result = runner.invoke(app, ["enrich", "foo.py", "bar"])
    result_stdout = json.load(result.stdout)
    diff = DeepDiff(result_stdout, expected_output)

    assert diff == {}
    assert result.exit_code == 0

def test_enrich_infers_path_to_nuanced_graph_failure():
    expected_output = 'Function definition for file path "foo.py" and function name "bar" not found\n'

    result = runner.invoke(app, ["enrich", "foo.py", "bar"])

    assert expected_output in result.stdout
    assert result.exit_code == 1
