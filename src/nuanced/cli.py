import json
import os
import typer
from rich import print
from nuanced import CodeGraph

app = typer.Typer()

@app.command()
def enrich(file_path: str, function_name: str):
    nuanced_graph_path = os.path.abspath(".nuanced/nuanced-graph.json")
    nuanced_graph_file = open(nuanced_graph_path, "r")
    call_graph = json.load(nuanced_graph_file)
    code_graph = CodeGraph(graph=call_graph)
    result = code_graph.enrich(file_path=file_path, function_name=function_name)

    if len(result.errors) > 0:
        for error in result.errors:
            print(str(error))
    elif not result.result:
        print(f"Function definition for file path \"{file_path}\" and function name \"{function_name}\" not found")
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
