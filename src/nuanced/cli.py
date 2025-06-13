import json
import os
import typer
from rich import print
from rich.console import Console
from nuanced import CodeGraph, __version__
from nuanced.code_graph import CodeGraphResult

app = typer.Typer()

ERROR_EXIT_CODE = 1


@app.command()
def enrich(
    file_path: str,
    function_name: str,
    include_builtins: bool = typer.Option(False, "--include-builtins"),
) -> None:
    err_console = Console(stderr=True)
    inferred_graph_dir = "."
    code_graph_result = CodeGraph.load(directory=inferred_graph_dir)

    if len(code_graph_result.errors) > 0:
        for error in code_graph_result.errors:
            err_console.print(str(error))
        raise typer.Exit(code=ERROR_EXIT_CODE)

    code_graph = code_graph_result.code_graph
    result = code_graph.enrich(
        file_path=file_path,
        function_name=function_name,
        include_builtins=include_builtins
    )

    if len(result.errors) > 0:
        for error in result.errors:
            err_console.print(str(error))
        raise typer.Exit(code=ERROR_EXIT_CODE)
    elif not result.result:
        err_msg = f"Function definition for file path \"{file_path}\" and function name \"{function_name}\" not found"
        err_console.print(err_msg)
        raise typer.Exit(code=ERROR_EXIT_CODE)
    else:
        print(json.dumps(result.result, indent=2))


@app.command()
def init(path: str) -> None:
    err_console = Console(stderr=True)
    abspath = os.path.abspath(path)
    print(f"Initializing {abspath}")
    result = CodeGraph.init(abspath)

    if len(result.errors) > 0:
        for error in result.errors:
            err_console.print(str(error))
    else:
        print("Done")

@app.callback(invoke_without_command=True)
def cli(
    ctx: typer.Context,
    version: bool = typer.Option(
        None,
        "-v",
        "--version",
        is_eager=True,
        help="Display nuanced version.",
    ),
):
    if version:
        print(f"nuanced {__version__}")
        raise typer.Exit()

def main() -> None:
    app()
