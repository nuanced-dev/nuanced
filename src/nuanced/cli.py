import json
import os
import typer
from pathlib import Path
from rich import print
from nuanced import CodeGraph

app = typer.Typer()

ERROR_EXIT_CODE = 1

@app.command()
def enrich(file_path: str, function_name: str):
    inferred_graph_dir = "."
    code_graph_result = CodeGraph.load(directory=inferred_graph_dir)

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
def init(path: str):
    abspath = os.path.abspath(path)
    print(f"Initializing {abspath}")
    result = CodeGraph.init(abspath)

    if len(result.errors) > 0:
        for error in result.errors:
            print(str(error))
    else:
        print("Done")

def main():
    app()
