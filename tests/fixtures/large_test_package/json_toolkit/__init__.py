from typing import Any, Dict

from .core.parser import Parser
from .core.transformer import transform_nested
from .utils.io import read_json_file, write_json_file

__all__ = ['Parser', 'transform_nested', 'read_json_file', 'write_json_file']

def quick_transform(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for simple transformations"""
    parser = Parser()
    if parser.validate(data):
        return transform_nested(data)
    return data
