import build.scip_pb2 as scip_pb
from .parse_symbol import parse_symbol, Suffix

def symbol_to_path(symbol_str: str) -> str:
    """Convert a SCIP symbol string to a fully qualified path"""
    symbol = parse_symbol(symbol_str)
    if not symbol.package:
        return symbol_str  # Handle local symbols

    # Build path components
    components = []

    # Add package name
    components.append(symbol.package.name)

    # Add descriptors in order, filtering for relevant types
    for desc in symbol.descriptors:
        if desc.suffix in (Suffix.Namespace, Suffix.Type, Suffix.Method, Suffix.Term):
            components.append(desc.name)

    return ".".join(components)
