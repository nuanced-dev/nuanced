import json
import os
import typer
from rich import print
from nuanced import CodeGraph
from nuanced.code_graph import CodeGraphResult

app = typer.Typer()

ERROR_EXIT_CODE = 1


@app.command()
def enrich(file_path: str, function_name: str) -> None:
    code_graph_result = _find_code_graph(file_path)

    if len(code_graph_result.errors) > 0:
        for error in code_graph_result.errors:
            print(str(error))
        raise typer.Exit(code=ERROR_EXIT_CODE)

    code_graph = code_graph_result.code_graph
    result = code_graph.enrich(file_path=file_path, function_name=function_name)

    if len(result.errors) > 0:
        for error in result.errors:
            print(str(error))
        raise typer.Exit(code=ERROR_EXIT_CODE)
    elif not result.result:
        print(f"Function definition for file path \"{file_path}\" and function name \"{function_name}\" not found")
        raise typer.Exit(code=ERROR_EXIT_CODE)
    else:
        print(json.dumps(result.result))


@app.command()
def init(path: str) -> None:
    abspath = os.path.abspath(path)
    print(f"Initializing {abspath}")
    result = CodeGraph.init(abspath)

    if len(result.errors) > 0:
        for error in result.errors:
            print(str(error))
    else:
        print("Done")


def _find_code_graph(file_path: str) -> CodeGraphResult:
    file_directory, _file_name = os.path.split(file_path)
    code_graph_result = CodeGraph.load(directory=file_directory)

    if len(code_graph_result.errors) > 0:
        top_directory = file_directory.split("/")[0]

        for root, dirs, _files in os.walk(top_directory, topdown=False):
            commonprefix = os.path.commonprefix([root, file_directory])

            if commonprefix == root and CodeGraph.NUANCED_DIRNAME in dirs:
                code_graph_result = CodeGraph.load(directory=root)
                break

    return code_graph_result


def main() -> None:
    app()
