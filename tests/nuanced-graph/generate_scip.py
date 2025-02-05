import os

# Import the generated SCIP protobuf module.
# Adjust the module path if required.
from nuanced_graph.build import scip_pb2 as scip


def write_fixture_class_to_scip():
    """
    Parses the fixture_class.py file and writes out a SCIP index protobuf.
    This is a hardcoded parser for testing purposes.
    """
    # Path to the fixture file
    fixture_path = os.path.join("tests", "fixtures", "test_package", "fixture_class.py")

    # Read the file content
    with open(fixture_path, "r") as f:
        file_text = f.read()

    # Create a SCIP Index message
    index = scip.Index()

    # Fill minimal metadata in the index
    index.metadata.version = scip.ProtocolVersion.UnspecifiedProtocolVersion
    index.metadata.tool_info.name = "test_tool"
    index.metadata.tool_info.version = "0.1"
    index.metadata.project_root = "tests/fixtures/"

    # Create a document for the fixture file
    doc = index.documents.add()
    doc.language = "python"
    doc.relative_path = fixture_path
    doc.text = file_text
    doc.position_encoding = scip.PositionEncoding.UTF8CodeUnitOffsetFromLineStart

    # --- Manually add symbol for the class FixtureClass ---
    symbol_info_class = doc.symbols.add()
    # The symbol string here is arbitrary; a trailing '#' is a common convention
    symbol_info_class.symbol = "py . fixture_class . FixtureClass#"
    symbol_info_class.display_name = "FixtureClass"
    # For demonstration, assume kind 7 means a class (per SCIP spec)
    symbol_info_class.kind = scip.SymbolInformation.Kind.Class

    symbol_info_foo = doc.symbols.add()
    symbol_info_foo.symbol = "py . fixture_class . FixtureClass#foo()."
    symbol_info_foo.display_name = "foo"
    symbol_info_foo.kind = scip.SymbolInformation.Kind.Method

    # --- Manually add symbol for function bar ---
    symbol_info_bar = doc.symbols.add()
    symbol_info_bar.symbol = "py . fixture_class . bar()."
    symbol_info_bar.display_name = "bar"
    # For demonstration, assume kind 17 means a function (this is arbitrary for our test)
    symbol_info_bar.kind = scip.SymbolInformation.Kind.Function

    symbol_info_bar_call_class = doc.symbols.add()
    symbol_info_bar_call_class.symbol = "py . fixture_class . FixtureClass#"
    symbol_info_bar_call_class.kind = scip.SymbolInformation.Kind.Class
    symbol_info_bar_call_class.relationships.add(
        symbol=symbol_info_class.symbol, is_definition=True
    )
    symbol_info_bar_call_class.enclosing_symbol = symbol_info_bar.symbol

    symbol_info_bar_call_foo = doc.symbols.add()
    symbol_info_bar_call_foo.symbol = "py . fixture_class . FixtureClass#foo()."
    symbol_info_bar_call_foo.kind = scip.SymbolInformation.Kind.Method
    symbol_info_bar_call_foo.relationships.add(
        symbol=symbol_info_foo.symbol, is_definition=True
    )
    symbol_info_bar_call_foo.enclosing_symbol = symbol_info_bar.symbol

    # Write the SCIP protobuf message to an output file.
    output_file = "tests/fixtures/test_package/fixture_class.scip"
    with open(output_file, "wb") as out:
        out.write(index.SerializeToString())

    print(f"SCIP index written to {output_file}")


if __name__ == "__main__":
    write_fixture_class_to_scip()
