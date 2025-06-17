from jarviscg import formats
from jarviscg.core import CallGraphGenerator
from nuanced.lib.utils import grouped_by_directory, grouped_by_package
import os


BUILTIN_FUNCTION_PREFIX = "<builtin>"

def generate(entry_points: list, **kwargs) -> dict:
    graph = {}
    files_by_package_dir = grouped_by_package(entry_points)
    flattened = set([item for sublist in files_by_package_dir.values() for item in sublist])
    modules_by_dir = grouped_by_directory(list(set(entry_points).difference(flattened)))

    for dir_path, file_paths in files_by_package_dir.items():
        package_call_graph = _generate_package_call_graph(
            file_paths=file_paths,
            package_dir_path=dir_path
        )
        graph.update(package_call_graph)

    for file_paths in modules_by_dir.values():
        modules_call_graph = _generate_modules_call_graph(file_paths=file_paths)
        modules_call_graph.update(graph)
        graph = modules_call_graph

    return graph

def _generate_package_call_graph(*, file_paths=list[str], package_dir_path: str) -> dict:
    package_path_parts = package_dir_path.split(os.sep)
    package_parent_path = os.sep.join(package_path_parts[0:-1])
    call_graph = CallGraphGenerator(
        file_paths,
        package_parent_path,
        decy=None,
        precision=None,
        moduleEntry=None,
    )
    call_graph.analyze()
    graph_root = os.getcwd()
    path_from_cwd_to_package_dir = os.path.relpath(package_dir_path, graph_root)
    scope_prefix = None

    if path_from_cwd_to_package_dir.count(os.sep) > 0:
        scope_prefix = path_from_cwd_to_package_dir.replace(os.sep, ".")

    formatter = formats.Nuanced(call_graph, scope_prefix=scope_prefix)
    return formatter.generate()

def _generate_modules_call_graph(*, file_paths=list[str]) -> dict:
    call_graph = CallGraphGenerator(
        file_paths,
        os.getcwd(),
        decy=None,
        precision=None,
        moduleEntry=None,
    )
    call_graph.analyze()

    formatter = formats.Nuanced(call_graph)
    return formatter.generate()
