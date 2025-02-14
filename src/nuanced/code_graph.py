from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import concurrent.futures
import glob
import json
import os
from nuanced.lib.call_graph import CallGraph

CodeGraphResult = namedtuple("CodeGraphResult", ["errors", "code_graph"])

class CodeGraph():
    ELIGIBLE_FILE_TYPE_PATTERN = "*.py"
    INIT_TIMEOUT_SECONDS = 30
    NUANCED_DIRNAME = ".nuanced"
    NUANCED_GRAPH_FILENAME = "nuanced-graph.json"

    @classmethod
    def init(cls, path: str) -> CodeGraphResult:
        errors = []
        absolute_path = os.path.abspath(path)

        if not os.path.isdir(absolute_path):
            errors.append(f"Directory not found: {absolute_path}")
            code_graph = None
        else:
            eligible_filepaths = glob.glob(
                    f'**/{cls.ELIGIBLE_FILE_TYPE_PATTERN}',
                    root_dir=absolute_path,
                    recursive=True
                )
            eligible_absolute_filepaths = [absolute_path + "/" + p for p in eligible_filepaths]
            if len(eligible_absolute_filepaths) == 0:
                errors.append(f"No eligible files found in {absolute_path}")
                code_graph = None
            else:
                with ThreadPoolExecutor() as executor:
                    call_graph = CallGraph(eligible_absolute_filepaths)
                    future = executor.submit(call_graph.generate)
                    done, not_done = wait([future], timeout=cls.INIT_TIMEOUT_SECONDS, return_when=FIRST_COMPLETED)

                    if future in done:
                        try:
                            call_graph_dict = call_graph.to_dict()
                            nuanced_dirpath = f'{absolute_path}/{cls.NUANCED_DIRNAME}'
                            os.mkdir(nuanced_dirpath, exist_ok=True)

                            nuanced_graph_file = open(f'{nuanced_dirpath}/{cls.NUANCED_GRAPH_FILENAME}', "w+")
                            nuanced_graph_file.write(json.dumps(call_graph_dict))

                            code_graph = cls(call_graph=call_graph_dict)
                        except Exception as e:
                            errors.append(str(e))
                            code_graph = None
                    else:
                        executor.shutdown(wait=False, cancel_futures=True)
                        errors.append("Timed out")
                        code_graph = None

        return CodeGraphResult(errors, code_graph)

    def __init__(self, call_graph=dict|None) -> None:
        self.call_graph = call_graph
