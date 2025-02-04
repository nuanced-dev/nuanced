import json
from typing import Any, Dict
from pathlib import Path

# Top level code
DEFAULT_ENCODING = 'utf-8'
DEFAULT_INDENT = 2

def read_json_file(filepath: str) -> Dict[str, Any]:
    """Read JSON from file"""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
        
    with open(path, 'r', encoding=DEFAULT_ENCODING) as f:
        return json.load(f)

def write_json_file(data: Dict[str, Any], filepath: str) -> None:
    """Write JSON to file"""
    path = Path(filepath)
    
    # Ensure directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding=DEFAULT_ENCODING) as f:
        json.dump(data, f, indent=DEFAULT_INDENT)
