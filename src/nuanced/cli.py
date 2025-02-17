import os
import typer
from nuanced import CodeGraph

app = typer.Typer()

@app.command()
def enrich(function_definition_path: str):
    print(f"Not implemented")

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
