from jarviscg import formats
from jarviscg.core import CallGraphGenerator

class CallGraph():
    def __init__(self, entry_points: list, **kwargs):
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
        self.call_graph = call_graph

    def generate(self) -> None:
        self.call_graph.analyze()

    def to_dict(self) -> dict:
        formatter = formats.Nuanced(self.call_graph)
        return formatter.generate()
