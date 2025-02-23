from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from itertools import groupby
import concurrent.futures
import errno
import glob
import json
import os
from nuanced.lib.call_graph import CallGraph

CodeGraphResult = namedtuple("CodeGraphResult", ["errors", "code_graph"])
EnrichmentResult = namedtuple("EnrichmentResult", ["errors", "result"])

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
            sorted_eligible_absolute_filepaths = sorted(eligible_absolute_filepaths, key=os.path.getmtime)

            if len(sorted_eligible_absolute_filepaths) == 0:
                error = ValueError(f"No eligible files found in {absolute_path}")
                errors.append(error)
                code_graph = None
            else:
                with ThreadPoolExecutor() as executor:
                    call_graph = CallGraph(sorted_eligible_absolute_filepaths)
                    future = executor.submit(call_graph.generate)
                    done, not_done = wait([future], timeout=cls.INIT_TIMEOUT_SECONDS, return_when=FIRST_COMPLETED)

                    if future in done:
                        try:
                            call_graph_dict = call_graph.to_dict()
                            nuanced_dirpath = f'{absolute_path}/{cls.NUANCED_DIRNAME}'
                            os.makedirs(nuanced_dirpath, exist_ok=True)

                            nuanced_graph_file = open(f'{nuanced_dirpath}/{cls.NUANCED_GRAPH_FILENAME}', "w+")
                            nuanced_graph_file.write(json.dumps(call_graph_dict))

                            code_graph = cls(graph=call_graph_dict)
                        except Exception as e:
                            errors.append(str(e))
                            code_graph = None
                    else:
                        executor.shutdown(wait=False, cancel_futures=True)
                        error = concurrent.futures.TimeoutError()
                        errors.append(error)
                        code_graph = None

        return CodeGraphResult(errors, code_graph)

    def __init__(self, graph:dict|None) -> None:
        self.graph = graph

    def enrich(self, file_path: str, function_name: str) -> EnrichmentResult:
        absolute_filepath = os.path.abspath(file_path)
        graph_nodes_grouped_by_filepath = {k: [v[0] for v in v] for k, v in groupby(self.graph.items(), lambda x: x[1]["filepath"])}
        entrypoint_node_key = None
        function_names = graph_nodes_grouped_by_filepath.get(absolute_filepath, [])
        entrypoint_node_keys = [n for n in function_names if n.endswith(function_name)]

        if len(entrypoint_node_keys) > 1:
            error = ValueError(f"Multiple definitions for {function_name} found in {file_path}: {', '.join(entrypoint_node_keys)}")
            return EnrichmentResult(errors=[error], result=None)

        if len(entrypoint_node_keys) == 0:
            return EnrichmentResult(errors=[], result=None)

        entrypoint_node_key = entrypoint_node_keys[0]
        subgraph = self._build_subgraph(entrypoint_node_key)

        return EnrichmentResult(errors=[], result=subgraph)

    def _build_subgraph(self, entrypoint_node_key: str) -> dict|None:
        subgraph = dict()
        visited = set()
        entrypoint_node = self.graph.get(entrypoint_node_key)

        if entrypoint_node:
            subgraph[entrypoint_node_key] = entrypoint_node
            callees = set(subgraph[entrypoint_node_key].get("callees"))
            visited.add(entrypoint_node_key)

            while len(callees) > 0:
                callee_function_path = callees.pop()

                if callee_function_path not in visited:
                    visited.add(callee_function_path)

                    if callee_function_path in self.graph:
                        subgraph[callee_function_path] = self.graph.get(callee_function_path)
                        callee_entry = subgraph.get(callee_function_path)

                        if callee_entry:
                            callee_callees = set(callee_entry["callees"])
                            callees.update(callee_callees)

            return subgraph
