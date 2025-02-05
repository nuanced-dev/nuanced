from pathlib import Path
from .build.scip_pb2 import (
    Index,
    Document,
    SymbolInformation,
)
from .types import (
    Repo,
    Package as NuancedPackage,
    ModuleAnnotation,
    FunctionAnnotation,
    CodeRange,
)
from .parse_symbol import parse_symbol, Suffix


def read_scip(path: Path) -> Index:
    with open(path, "rb") as f:
        return Index.FromString(f.read())


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


def convert_document(doc: Document, package: NuancedPackage) -> ModuleAnnotation:
    """Convert a SCIP Document to a ModuleAnnotation"""
    module = ModuleAnnotation(
        package=package, module_path=doc.relative_path, functions=[]
    )

    # Process all symbols in the document
    for symbol in doc.symbols:
        # Skip non-function symbols
        if symbol.kind not in (
            SymbolInformation.Kind.Function,
            SymbolInformation.Kind.Method,
            SymbolInformation.Kind.StaticMethod,
        ):
            continue

        # Get the symbol path
        symbol_path = symbol_to_path(symbol.symbol)

        # Find all relationships that are references (calls to other functions)
        callees = set()
        for rel in symbol.relationships:
            if rel.is_reference:
                callee_path = symbol_to_path(rel.symbol)
                callees.add(callee_path)

        # Create function annotation
        func = FunctionAnnotation(
            module=module,
            path=symbol_path,
            digest="",  # We don't have this information in SCIP
            line_numbers=CodeRange(
                begin=0,  # These would need to come from Occurrences if we used them
                end=0,
            ),
            callees=callees,
        )

        module.functions.append(func)

    return module


def convert_index(index: Index, repo_path: Path) -> Repo:
    """Convert a SCIP Index to a Repo"""
    repo = Repo(packages=[])

    # Group documents by package
    docs_by_package = {}
    for doc in index.documents:
        # Extract package from first symbol in document
        package_path = None
        for symbol in doc.symbols:
            try:
                parsed = parse_symbol(symbol.symbol)
                if parsed.package:
                    package_path = Path(parsed.package.name)
                    break
            except ValueError:
                continue

        if package_path:
            if package_path not in docs_by_package:
                docs_by_package[package_path] = []
            docs_by_package[package_path].append(doc)

    # Convert each package
    for package_path, docs in docs_by_package.items():
        package = NuancedPackage(
            repo=repo, repo_path=repo_path / package_path, modules=[]
        )

        # Convert each document in the package
        for doc in docs:
            module = convert_document(doc, package)
            package.modules.append(module)

        repo.packages.append(package)

    return repo
