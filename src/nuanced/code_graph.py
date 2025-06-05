from collections import namedtuple
from itertools import groupby
from pathlib import Path
import errno
import glob
import json
import os
from nuanced.lib import call_graph
from nuanced.lib.utils import with_timeout

CodeGraphResult = namedtuple("CodeGraphResult", ["errors", "code_graph"])
EnrichmentResult = namedtuple("EnrichmentResult", ["errors", "result"])


class CodeGraph():
    ELIGIBLE_FILE_TYPE_PATTERN = "*.py"
    INIT_TIMEOUT_SECONDS = 60
    NUANCED_DIRNAME = ".nuanced"
    NUANCED_GRAPH_FILENAME = "nuanced-graph.json"

    @classmethod
    def init(cls, path: str) -> CodeGraphResult:
        errors = []
        code_graph = None
        absolute_path_to_package = os.path.abspath(path)

        if not os.path.isdir(absolute_path_to_package):
            error = FileNotFoundError(
                errno.ENOENT,
                os.strerror(errno.ENOENT),
                absolute_path_to_package
            )
            errors.append(error)
        else:
            eligible_filepaths = glob.glob(
                    f'**/{cls.ELIGIBLE_FILE_TYPE_PATTERN}',
                    root_dir=absolute_path_to_package,
                    recursive=True
                )
            eligible_absolute_filepaths = [absolute_path_to_package + "/" + p for p in eligible_filepaths]

            if len(eligible_absolute_filepaths) == 0:
                error = ValueError(f"No eligible files found in {absolute_path_to_package}")
                errors.append(error)
            elif f"{absolute_path_to_package}/__init__.py" not in eligible_absolute_filepaths:
                error = ValueError(f"No package definition found in {absolute_path_to_package}: `__init__.py` missing")
                errors.append(error)
            else:
                call_graph_result = with_timeout(
                    target=call_graph.generate,
                    args=(eligible_absolute_filepaths),
                    kwargs=({"package_path": absolute_path_to_package}),
                    timeout=cls.INIT_TIMEOUT_SECONDS,
                )
                call_graph_dict = call_graph_result.value

                if len(call_graph_result.errors) > 0:
                    errors = errors + call_graph_result.errors

                if call_graph_dict:
                    nuanced_dirpath = f'{absolute_path_to_package}/{cls.NUANCED_DIRNAME}'
                    os.makedirs(nuanced_dirpath, exist_ok=True)

                    nuanced_graph_file = open(f'{nuanced_dirpath}/{cls.NUANCED_GRAPH_FILENAME}', "w+")
                    nuanced_graph_file.write(json.dumps(call_graph_dict))
                    code_graph = cls(graph=call_graph_dict)

        return CodeGraphResult(code_graph=code_graph, errors=errors)

    @classmethod
    def load(cls, directory=str) -> CodeGraphResult:
        errors = []
        code_graph = None
        dir_path = Path(directory)
        file_paths = list(dir_path.glob(f"**/{cls.NUANCED_DIRNAME}/{cls.NUANCED_GRAPH_FILENAME}"))

        if len(file_paths) > 1:
            graph_file_paths = ", ".join([str(fp) for fp in file_paths])
            error = ValueError(f"Multiple Nuanced Graphs found in {os.path.abspath(directory)}: {graph_file_paths}")
            errors.append(error)
        elif len(file_paths) == 1:
            file_path = file_paths[0]
            graph_file = open(file_path, "r")
            graph = json.load(graph_file)
            code_graph = CodeGraph(graph=graph)
        elif len(file_paths) == 0:
            error = FileNotFoundError(f"Nuanced Graph not found in {os.path.abspath(directory)}")
            errors.append(error)

        return CodeGraphResult(code_graph=code_graph, errors=errors)

    def __init__(self, graph: dict | None) -> None:
        self.graph = graph

    def enrich(
        self,
        file_path: str,
        function_name: str,
        include_builtins: bool=False,
    ) -> EnrichmentResult:
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
        enriched_subgraph = {}

        for node_name, node_attrs in subgraph.items():
            if include_builtins:
                callees = node_attrs["callees"]
            else:
                callees = [c for c in node_attrs["callees"] if not c.startswith(call_graph.BUILTIN_FUNCTION_PREFIX)]

            enriched_node_attrs = {
                "filepath": node_attrs["filepath"],
                "callees": callees,
                "lineno": node_attrs.get("lineno", None),
                "end_lineno": node_attrs.get("end_lineno", None),
            }

            enriched_subgraph[node_name] = enriched_node_attrs

        return EnrichmentResult(errors=[], result=enriched_subgraph)

    def _build_subgraph(self, entrypoint_node_key: str) -> dict | None:
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
