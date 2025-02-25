from jarviscg import formats
from jarviscg.core import CallGraphGenerator

def generate(entry_points: list, **kwargs):
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
    args.update(kwargs)

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
