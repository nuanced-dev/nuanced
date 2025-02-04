from nuanced_graph.build.scip_pb2 import (
    Index,
    Metadata,
    ToolInfo,
    ProtocolVersion,
    TextEncoding,
    Document,
    SymbolInformation,
    Relationship,
)
import os


def test_scip_roundtrip(tmp_path):
    # Create a simple SCIP index
    index = Index()
    index.metadata.version = ProtocolVersion.UnspecifiedProtocolVersion
    index.metadata.project_root = "test/project"
    index.metadata.text_document_encoding = TextEncoding.UTF8

    tool_info = ToolInfo()
    tool_info.name = "test-indexer"
    tool_info.version = "1.0.0"
    tool_info.arguments.extend(["--test-arg"])
    index.metadata.tool_info.CopyFrom(tool_info)

    # Create first document - a class with a method
    doc1 = Document()
    doc1.language = "python"
    doc1.relative_path = "src/example/foo.py"

    # Class symbol
    class_symbol = SymbolInformation()
    class_symbol.symbol = "python . example 0.1.0 example/foo#Foo."
    class_symbol.kind = SymbolInformation.Kind.Class

    # Method symbol
    method_symbol = SymbolInformation()
    method_symbol.symbol = "python . example 0.1.0 example/foo#Foo.bar()."
    method_symbol.kind = SymbolInformation.Kind.Method
    method_symbol.enclosing_symbol = class_symbol.symbol

    doc1.symbols.extend([class_symbol, method_symbol])

    # Create second document - an interface implementation
    doc2 = Document()
    doc2.language = "python"
    doc2.relative_path = "src/example/bar.py"

    # Interface implementation class
    impl_class_symbol = SymbolInformation()
    impl_class_symbol.symbol = "python . example 0.1.0 example/bar#Bar."
    impl_class_symbol.kind = SymbolInformation.Kind.Class

    # Add relationship to first document's class
    relationship = Relationship()
    relationship.symbol = class_symbol.symbol
    relationship.is_implementation = True
    impl_class_symbol.relationships.extend([relationship])

    # Implementation method
    impl_method_symbol = SymbolInformation()
    impl_method_symbol.symbol = "python . example 0.1.0 example/bar#Bar.bar()."
    impl_method_symbol.kind = SymbolInformation.Kind.Method
    impl_method_symbol.enclosing_symbol = impl_class_symbol.symbol

    # Add relationship to first document's method
    method_relationship = Relationship()
    method_relationship.symbol = method_symbol.symbol
    method_relationship.is_implementation = True
    method_relationship.is_reference = True
    impl_method_symbol.relationships.extend([method_relationship])

    doc2.symbols.extend([impl_class_symbol, impl_method_symbol])

    # Add documents to index
    index.documents.extend([doc1, doc2])

    # Write to disk
    output_path = os.path.join(tmp_path, "test.scip")
    with open(output_path, "wb") as f:
        f.write(index.SerializeToString())

    # Read back and verify
    with open(output_path, "rb") as f:
        loaded_index = Index()
        loaded_index.ParseFromString(f.read())

    # Verify the contents match
    assert loaded_index.metadata.version == ProtocolVersion.UnspecifiedProtocolVersion
    assert loaded_index.metadata.project_root == "test/project"
    assert loaded_index.metadata.text_document_encoding == TextEncoding.UTF8
    assert loaded_index.metadata.tool_info.name == "test-indexer"
    assert loaded_index.metadata.tool_info.version == "1.0.0"
    assert list(loaded_index.metadata.tool_info.arguments) == ["--test-arg"]

    # Verify documents
    assert len(loaded_index.documents) == 2

    # Verify first document
    loaded_doc1 = loaded_index.documents[0]
    assert loaded_doc1.language == "python"
    assert loaded_doc1.relative_path == "src/example/foo.py"
    assert len(loaded_doc1.symbols) == 2
    assert loaded_doc1.symbols[0].symbol == "python . example 0.1.0 example/foo#Foo."
    assert (
        loaded_doc1.symbols[1].symbol == "python . example 0.1.0 example/foo#Foo.bar()."
    )
    assert loaded_doc1.symbols[1].enclosing_symbol == loaded_doc1.symbols[0].symbol

    # Verify second document
    loaded_doc2 = loaded_index.documents[1]
    assert loaded_doc2.language == "python"
    assert loaded_doc2.relative_path == "src/example/bar.py"
    assert len(loaded_doc2.symbols) == 2
    assert len(loaded_doc2.symbols[0].relationships) == 1
    assert (
        loaded_doc2.symbols[0].relationships[0].symbol == loaded_doc1.symbols[0].symbol
    )
    assert loaded_doc2.symbols[0].relationships[0].is_implementation
    assert len(loaded_doc2.symbols[1].relationships) == 1
    assert (
        loaded_doc2.symbols[1].relationships[0].symbol == loaded_doc1.symbols[1].symbol
    )
    assert loaded_doc2.symbols[1].relationships[0].is_implementation
    assert loaded_doc2.symbols[1].relationships[0].is_reference
