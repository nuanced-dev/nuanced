from collections import namedtuple
import glob
import json
import os
from nuanced.lib.call_graph import CallGraph

CodeGraphResult = namedtuple("CodeGraphResult", ["errors", "code_graph"])

class CodeGraph():
    ELIGIBLE_FILE_TYPE_PATTERN = "*.py"

    @classmethod
    def init(cls, path: str) -> CodeGraphResult:
        errors = []
        absolute_path = os.path.abspath(path)
        nuanced_dirpath = f'{absolute_path}/.nuanced'
        os.mkdir(nuanced_dirpath)

        eligible_filepaths = glob.glob(
                f'**/{cls.ELIGIBLE_FILE_TYPE_PATTERN}',
                root_dir=absolute_path,
                recursive=True
            )
        eligible_absolute_filepaths = [absolute_path + "/" + p for p in eligible_filepaths]

        call_graph = CallGraph(eligible_absolute_filepaths)
        call_graph.generate()
        call_graph_dict = call_graph.to_dict()

        nuanced_graph_file = open(f'{nuanced_dirpath}/nuanced-graph.json', "w+")
        nuanced_graph_file.write(json.dumps(call_graph_dict))

        code_graph = cls(call_graph=call_graph_dict)
        return CodeGraphResult(errors, code_graph)

    def __init__(self, call_graph=dict|None) -> None:
        self.call_graph = call_graph
