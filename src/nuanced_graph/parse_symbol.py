from enum import IntEnum
from typing import List, Optional
from pydantic import BaseModel


class Suffix(IntEnum):
    UnspecifiedSuffix = 0
    Namespace = 1
    Type = 2
    Term = 3
    Method = 4
    TypeParameter = 5
    Parameter = 6
    Meta = 7
    Local = 8
    Macro = 9


class Package(BaseModel):
    manager: str
    name: str
    version: str


class Descriptor(BaseModel):
    name: str
    disambiguator: str = ""
    suffix: Suffix


class Symbol(BaseModel):
    scheme: str = ""
    package: Optional[Package] = None
    descriptors: List[Descriptor]


def parse_escaped_token(s, pos):
    token = []
    while pos < len(s):
        if s[pos] == " ":
            if pos + 1 < len(s) and s[pos + 1] == " ":
                token.append(" ")
                pos += 2
            else:
                break
        else:
            token.append(s[pos])
            pos += 1
    return "".join(token), pos


def parse_identifier(s, pos):
    if pos >= len(s):
        raise ValueError("Expected identifier at pos")
    if s[pos] == "`":
        pos += 1
        chars = []
        while pos < len(s):
            if s[pos] == "`":
                if pos + 1 < len(s) and s[pos + 1] == "`":
                    chars.append("`")
                    pos += 2
                else:
                    pos += 1
                    return "".join(chars), pos
            else:
                chars.append(s[pos])
                pos += 1
        raise ValueError("Unterminated escaped identifier")
    start = pos
    allowed = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_+-$"
    while pos < len(s) and s[pos] in allowed:
        pos += 1
    if pos == start:
        raise ValueError("Expected simple identifier at pos")
    return s[start:pos], pos


def parse_simple_identifier(s, pos):
    start = pos
    allowed = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_+-$"
    while pos < len(s) and s[pos] in allowed:
        pos += 1
    if pos == start:
        raise ValueError("Expected simple identifier at pos")
    return s[start:pos], pos


def parse_descriptor(s, pos):
    if pos >= len(s):
        raise ValueError("Expected descriptor at pos")
    if s[pos] == "[":
        pos += 1
        name, pos = parse_identifier(s, pos)
        if pos >= len(s) or s[pos] != "]":
            raise ValueError("Expected ']'")
        pos += 1
        return Descriptor(name=name, suffix=Suffix.TypeParameter), pos
    elif s[pos] == "(":
        pos += 1
        name, pos = parse_identifier(s, pos)
        if pos >= len(s) or s[pos] != ")":
            raise ValueError("Expected ')'")
        pos += 1
        return Descriptor(name=name, suffix=Suffix.Parameter), pos
    else:
        name, pos = parse_identifier(s, pos)
        if pos < len(s) and s[pos] == "(":
            pos += 1
            disambiguator = ""
            if pos < len(s) and s[pos] != ")":
                disambiguator, pos = parse_simple_identifier(s, pos)
            if pos >= len(s) or s[pos] != ")":
                raise ValueError("Expected ')' in method descriptor")
            pos += 1
            if pos >= len(s) or s[pos] != ".":
                raise ValueError("Expected '.' after method descriptor")
            pos += 1
            return Descriptor(
                name=name, disambiguator=disambiguator, suffix=Suffix.Method
            ), pos
        if pos >= len(s):
            raise ValueError("Expected descriptor punctuation")
        punct = s[pos]
        pos += 1
        if punct == "/":
            suf = Suffix.Namespace
        elif punct == "#":
            suf = Suffix.Type
        elif punct == ".":
            suf = Suffix.Term
        elif punct == ":":
            suf = Suffix.Meta
        elif punct == "!":
            suf = Suffix.Macro
        else:
            raise ValueError("Unexpected descriptor punctuation: " + punct)
        return Descriptor(name=name, suffix=suf), pos


def parse_symbol(symbol_str: str) -> Symbol:
    if symbol_str.startswith("local "):
        local_id = symbol_str[len("local ") :]
        allowed = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_+-$"
        if not local_id or any(c not in allowed for c in local_id):
            raise ValueError("Invalid local id")
        return Symbol(descriptors=[Descriptor(name=local_id, suffix=Suffix.Local)])
    pos = 0
    scheme, pos = parse_escaped_token(symbol_str, pos)
    if not scheme or scheme.startswith("local"):
        raise ValueError("Invalid scheme")
    if pos >= len(symbol_str) or symbol_str[pos] != " ":
        raise ValueError("Expected space after scheme")
    pos += 1
    manager, pos = parse_escaped_token(symbol_str, pos)
    if pos >= len(symbol_str) or symbol_str[pos] != " ":
        raise ValueError("Expected space after manager")
    pos += 1
    pkg_name, pos = parse_escaped_token(symbol_str, pos)
    if pos >= len(symbol_str) or symbol_str[pos] != " ":
        raise ValueError("Expected space after package-name")
    pos += 1
    version, pos = parse_escaped_token(symbol_str, pos)
    if pos >= len(symbol_str) or symbol_str[pos] != " ":
        raise ValueError("Expected space before descriptors")
    pos += 1
    pkg = Package(manager=manager, name=pkg_name, version=version)
    descriptors = []
    while pos < len(symbol_str):
        if symbol_str[pos] == " ":
            pos += 1
            continue
        desc, pos = parse_descriptor(symbol_str, pos)
        descriptors.append(desc)
    if not descriptors:
        raise ValueError("No descriptors found")
    return Symbol(scheme=scheme, package=pkg, descriptors=descriptors)
