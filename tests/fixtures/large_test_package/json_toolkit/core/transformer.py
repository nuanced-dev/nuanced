from typing import Any, Dict, List, Union
from copy import deepcopy

def transform_nested(data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform a nested JSON structure"""
    result = {}
    
    for key, value in data.items():
        transformed = transform_element(value)
        if transformed is not None:
            result[key] = transformed
            
    return result

def transform_element(element: Union[Dict, List, Any]) -> Any:
    """Transform a single element, which might be nested"""
    if isinstance(element, dict):
        return transform_nested(element)
    elif isinstance(element, list):
        return [transform_element(item) for item in element]
    elif isinstance(element, str):
        return _process_string(element)
    else:
        return element

def _process_string(s: str) -> str:
    """Internal helper for string processing"""
    def process_part(part: str) -> str:
        # Nested function example
        return part.strip().lower()
    
    return " ".join(process_part(part) for part in s.split())
