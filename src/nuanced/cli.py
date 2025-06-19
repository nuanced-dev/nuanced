import json
import os
import typer
from rich import print
from rich.console import Console
from nuanced import CodeGraph, __version__
from nuanced.code_graph import CodeGraphResult, DEFAULT_INIT_TIMEOUT_SECONDS
from typing_extensions import Annotated, Optional


typer.rich_utils.STYLE_NEGATIVE_SWITCH = "bold indian_red"
typer.rich_utils.STYLE_DEPRECATED = "indian_red"
typer.rich_utils.STYLE_REQUIRED_SHORT = "indian_red"
typer.rich_utils.STYLE_REQUIRED_LONG = "dim indian_red"
typer.rich_utils.STYLE_ERRORS_PANEL_BORDER = "indian_red"
typer.rich_utils.STYLE_ABORTED = "indian_red"
typer.rich_utils.STYLE_OPTION = "bold deep_sky_blue1"
typer.rich_utils.STYLE_COMMANDS_TABLE_FIRST_COLUMN = "bold medium_orchid"
typer.rich_utils.STYLE_METAVAR = "bold medium_orchid"
typer.rich_utils.STYLE_USAGE = "medium_orchid"
typer.rich_utils.STYLE_OPTION_ENVVAR = "dim deep_sky_blue1"
typer.rich_utils.STYLE_SWITCH = "bold plum1"

app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    help="Python code intelligence for agentic developer workflows."
)

ERROR_EXIT_CODE = 1


@app.command(help="Enrich a function and its callees and print enriched function call graph as JSON.")
def enrich(
    file_path: Annotated[str, typer.Argument(help="Path to file containing function definition.")],
    function_name: Annotated[str, typer.Argument(help="Partial or fully qualified name of function.")],
    include_builtins: Annotated[bool, typer.Option("--include-builtins", help="Include callees defined in Python's builtins module.")] = False,
) -> None:
    err_console = Console(stderr=True)
    code_graph_result = _find_code_graph(file_path)

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


@app.command(help="Initialize analysis.")
def init(
   path: Annotated[str, typer.Argument(help="Path to directory containing Python code.")],
   timeout_seconds: Annotated[Optional[int], typer.Option("--timeout-seconds", "-t", help="Timeout in seconds.")]=DEFAULT_INIT_TIMEOUT_SECONDS
) -> None:
    err_console = Console(stderr=True)
    abspath = os.path.abspath(path)
    print(f"Initializing {abspath}")
    result = CodeGraph.init(abspath, timeout_seconds=timeout_seconds)

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

def _find_code_graph(file_path: str) -> CodeGraphResult:
    code_graph_result = CodeGraph.load(directory=os.getcwd())

    if len(code_graph_result.errors) > 0:
        file_directory, _file_name = os.path.split(file_path)
        top_directory = file_directory.split("/")[0]

        for root, dirs, _files in os.walk(top_directory, topdown=False):
            commonprefix = os.path.commonprefix([root, file_directory])

            if commonprefix == root and CodeGraph.NUANCED_DIRNAME in dirs:
                code_graph_result = CodeGraph.load(directory=root)
                break

    return code_graph_result

def main() -> None:
    app()
