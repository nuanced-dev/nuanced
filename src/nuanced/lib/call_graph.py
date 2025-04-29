from jarviscg import formats
from jarviscg.core import CallGraphGenerator


def generate(entry_points: list, **kwargs) -> dict:
    default_package = None
    default_decy = False
    default_precision = False
    default_module_entry = None

    args = {
        "package": default_package,
        "decy": default_decy,
        "precision": default_precision,
        "moduleEntry": default_module_entry,
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
