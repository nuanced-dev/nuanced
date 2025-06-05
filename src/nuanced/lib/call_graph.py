from jarviscg import formats
from jarviscg.core import CallGraphGenerator


BUILTIN_FUNCTION_PREFIX = "<builtin>"

def generate(entry_points: list, **kwargs) -> dict:
    args = {
        "package": None,
        "decy": False,
        "precision": False,
        "moduleEntry": None,
    }
    package_path = kwargs.get("package_path", None)

    if package_path:
        package_path_parts = package_path.split("/")
        package_parent_path = "/".join(package_path_parts[0:-1])
        args["package"] = package_parent_path

    call_graph = CallGraphGenerator(
        entry_points,
        args["package"],
        decy=args["decy"],
        precision=args["precision"],
        moduleEntry=args["moduleEntry"],
    )
    call_graph.analyze()

    formatter = formats.Nuanced(call_graph)
    call_graph_dict = formatter.generate()
    return call_graph_dict
