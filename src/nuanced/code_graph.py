from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import concurrent.futures
import errno
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
            error = FileNotFoundError(
                errno.ENOENT,
                os.strerror(errno.ENOENT),
                absolute_path
            )
            errors.append(error)
            code_graph = None
        else:
            eligible_filepaths = glob.glob(
                    f'**/{cls.ELIGIBLE_FILE_TYPE_PATTERN}',
                    root_dir=absolute_path,
                    recursive=True
                )
            eligible_absolute_filepaths = [absolute_path + "/" + p for p in eligible_filepaths]
            if len(eligible_absolute_filepaths) == 0:
                error = ValueError(f"No eligible files found in {absolute_path}")
                errors.append(error)
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
                        error = concurrent.futures.TimeoutError()
                        errors.append(error)
                        code_graph = None

        return CodeGraphResult(errors, code_graph)

    def __init__(self, call_graph:dict|None) -> None:
        self.call_graph = call_graph

    def enrich(self, function_path: str) -> dict|None:
        subgraph = dict()
        visited = set()
        function_entry = self.call_graph.get(function_path)

        if function_entry:
            subgraph[function_path] = function_entry
            callees = set(subgraph[function_path].get("callees"))
            visited.add(function_path)

            while len(callees) > 0:
                callee_function_path = callees.pop()

                if callee_function_path not in visited:
                    visited.add(callee_function_path)

                    if callee_function_path in self.call_graph:
                        subgraph[callee_function_path] = self.call_graph.get(callee_function_path)
                        callee_entry = subgraph.get(callee_function_path)

                        if callee_entry:
                            callee_callees = set(callee_entry["callees"])
                            callees.update(callee_callees)

            return subgraph
