from pathlib import Path
from typing import Callable
from pydantic import BaseModel
from abc import ABCMeta, abstractmethod


class FunctionProperties(BaseModel, metaclass=ABCMeta):
    """
    This is an abstract base class that all function properties will inherit from.  Protocols are not supported by pydantic.
    """

    property_name: str

    @abstractmethod
    def text_rep(self, function_name: str) -> str:
        # a text representaiton of this property
        ...


class CodeRange(BaseModel):
    """
    This will probably need to eventually be something more fine-grained.
    giving column information as well as line number information.

    But for now this works.
    """

    begin: int
    end: int


class FunctionAnnotation(BaseModel):
    """
    This very loosely corresponds to the SCIP "symbolinformation" type.
    At the moment, I don't think we need a concept of a "class" (though SCIP has that concept through the use of "enclosing_symbol")
    """

    module: "ModuleAnnotation"  # a back reference to the module that this is a part of.
    path: str  # this is in relationship to the module path.  "" (empty) is the module itself.
    digest: str  # this is a hash of the text of the function
    # later we can add ast hash's as body digests to recognize functions that change names
    # but at the moment, we don't need to worry about this.
    line_numbers: (
        CodeRange  # the location in the file that this function definition is at.
    )

    # we are going to need to map invocations to callee, so this `str` might get updated
    # to a type
    callees: set[str]  # fully_qualified paths of each function this calls.

    # We can iterate and generate annotations across properties.
    properties: list[FunctionProperties] | None = None

    def generate_annotation(self) -> str:
        """
        This is a super simple generate annotations function.

        It will output each property's representation in a line on it's own.

        # property_output_1
        # property_output_2
        """
        if self.properties is None:
            return ""
        annotations = []
        for property in self.properties:
            annotations.append("# " + property.text_rep(self.path))

        return "\n".join(annotations)


class ModuleAnnotation(BaseModel):
    """This corresponds to a "document" in SCIP"""

    package: "Package"  # a back-reference to the package this is a part of.
    module_path: str  # this is the module path in relation to the package path.

    # these might be best as a dict (this one and the one in Package and Repo)
    functions: list[
        FunctionAnnotation
    ]  # the `._module` function is all the code that is not in a function.

    def __getitem__(self, path: str) -> FunctionAnnotation:
        """This is a helper function to get a function from the module by it's path"""
        for f in self.functions:
            if f.path == path:
                return f
        raise ValueError(f"Function {path} not found in module {self.module_path}")


class Package(BaseModel):
    repo: "Repo"  # a back reference to the repo this is a part of.
    repo_path: Path  # this is in relationship to the repo root.
    modules: list[ModuleAnnotation]  # these are all the modules in the package.


class Repo(BaseModel):
    packages: list[Package]


# an Annotator is just a function that takes a `FunctionAnnotation` object, and returns a `FunctionProperties` object for that annotation.
# the back references in `FunctionAnnoation` et. al. allow the
# annotator to walk the graph.
Annotator = Callable[[FunctionAnnotation], FunctionProperties]
