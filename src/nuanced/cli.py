import json
import os
import typer
from nuanced import CodeGraph

app = typer.Typer()

@app.command()
def enrich(function_definition_path: str):
    nuanced_graph_path = os.path.abspath(".nuanced/nuanced-graph.json")
    nuanced_graph_file = open(nuanced_graph_path, "r")
    call_graph = json.load(nuanced_graph_file)
    code_graph = CodeGraph(call_graph=call_graph)
    result = code_graph.enrich(function_definition_path)

    if not result:
        print(f"\"{function_definition_path}\" not found")
    else:
        print(json.dumps(result))

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
