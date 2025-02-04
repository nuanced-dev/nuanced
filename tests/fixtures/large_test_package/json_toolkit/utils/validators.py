from typing import Any

def is_valid_json_structure(data: Any) -> bool:
    """Validate JSON structure"""
    if isinstance(data, dict):
        return all(isinstance(k, str) and is_valid_json_structure(v) for k, v in data.items())
    elif isinstance(data, list):
        return all(is_valid_json_structure(item) for item in data)
    elif isinstance(data, (str, int, float, bool)) or data is None:
        return True
    return False
