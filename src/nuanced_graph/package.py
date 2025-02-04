from pydantic import BaseModel
from .types import CodeRange
from pathlib import Path
from typing import Self


class Function(BaseModel):
    local_name: str
    fully_qualified_name: str
    code_loc: CodeRange

    def get_code(self) -> Self:
        ...

class Module(BaseModel):
    """

    """
    path: Path
    name: str
    functions: list[Function]

    def get(self) -> Self:
        ...

class Package(BaseModel):
    path: Path
    name: str
    modules: list[Module]


# how this works:

# nuanced init <package_path>j
