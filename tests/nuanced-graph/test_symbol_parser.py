import pytest
from src.nuanced_graph.parse_symbol import parse_symbol, Suffix


def test_local_symbol_valid():
    sym = parse_symbol("local x123")
    assert sym.scheme == ""
    assert sym.package is None
    assert len(sym.descriptors) == 1
    assert sym.descriptors[0].name == "x123"
    assert sym.descriptors[0].suffix == Suffix.Local


@pytest.mark.parametrize("s", ["local x 123", "local "])
def test_local_symbol_invalid(s):
    with pytest.raises(ValueError):
        parse_symbol(s)


def test_global_symbol_basic():
    s = "scheme manager pkg version Foo/"
    sym = parse_symbol(s)
    assert sym.scheme == "scheme"
    assert sym.package is not None
    assert sym.package.manager == "manager"
    assert sym.package.name == "pkg"
    assert sym.package.version == "version"
    assert len(sym.descriptors) == 1
    assert sym.descriptors[0].name == "Foo"
    assert sym.descriptors[0].suffix == Suffix.Namespace


def test_global_symbol_multiple_descriptors():
    s = "myscheme mymanager mypkg 1.0 Foo/Bar#Baz.Qux:Quux!doSomething().doSomething(foo).[T](p)"
    sym = parse_symbol(s)
    assert sym.scheme == "myscheme"
    assert sym.package is not None
    assert sym.package.manager == "mymanager"
    assert sym.package.name == "mypkg"
    assert sym.package.version == "1.0"
    assert len(sym.descriptors) == 9
    assert sym.descriptors[0].name == "Foo"
    assert sym.descriptors[0].suffix == Suffix.Namespace
    assert sym.descriptors[1].name == "Bar"
    assert sym.descriptors[1].suffix == Suffix.Type
    assert sym.descriptors[2].name == "Baz"
    assert sym.descriptors[2].suffix == Suffix.Term
    assert sym.descriptors[3].name == "Qux"
    assert sym.descriptors[3].suffix == Suffix.Meta
    assert sym.descriptors[4].name == "Quux"
    assert sym.descriptors[4].suffix == Suffix.Macro
    assert sym.descriptors[5].name == "doSomething"
    assert sym.descriptors[5].disambiguator == ""
    assert sym.descriptors[5].suffix == Suffix.Method
    assert sym.descriptors[6].name == "doSomething"
    assert sym.descriptors[6].disambiguator == "foo"
    assert sym.descriptors[6].suffix == Suffix.Method
    assert sym.descriptors[7].name == "T"
    assert sym.descriptors[7].suffix == Suffix.TypeParameter
    assert sym.descriptors[8].name == "p"
    assert sym.descriptors[8].suffix == Suffix.Parameter


def test_global_symbol_escaped_tokens():
    s = "my  scheme my  manager my  pkg 1.0 Foo/"
    sym = parse_symbol(s)
    assert sym.scheme == "my scheme"
    assert sym.package is not None
    assert sym.package.manager == "my manager"
    assert sym.package.name == "my pkg"


def test_global_symbol_escaped_identifier_in_descriptor():
    s = "s m p v `Hello``World`#"
    sym = parse_symbol(s)
    assert len(sym.descriptors) == 1
    assert sym.descriptors[0].name == "Hello`World"
    assert sym.descriptors[0].suffix == Suffix.Type


def test_method_descriptor_no_disambiguator():
    s = "s m p v doSomething()."
    sym = parse_symbol(s)
    assert len(sym.descriptors) == 1
    assert sym.descriptors[0].name == "doSomething"
    assert sym.descriptors[0].disambiguator == ""
    assert sym.descriptors[0].suffix == Suffix.Method


def test_method_descriptor_with_disambiguator():
    s = "s m p v doSomething(foo)."
    sym = parse_symbol(s)
    assert len(sym.descriptors) == 1
    assert sym.descriptors[0].name == "doSomething"
    assert sym.descriptors[0].disambiguator == "foo"
    assert sym.descriptors[0].suffix == Suffix.Method


@pytest.mark.parametrize(
    "s",
    [
        "s m p v Foo",
        "s m p v doSomething(foo.",
        "s m p v doSomething(foo)",
        "s m p v [T",
        "s m p v `unterminated Foo/",
    ],
)
def test_error_cases(s):
    with pytest.raises(ValueError):
        parse_symbol(s)


def test_error_invalid_scheme():
    s = "localSomething m p v Foo/"
    with pytest.raises(ValueError):
        parse_symbol(s)
