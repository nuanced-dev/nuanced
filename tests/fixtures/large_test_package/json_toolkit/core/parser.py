from typing import Any, Dict, Optional
from dataclasses import dataclass
from ..utils.validators import is_valid_json_structure

@dataclass
class ValidationResult:
    is_valid: bool
    error_message: Optional[str] = None

class Parser:
    """JSON parser with validation capabilities"""
    
    def __init__(self, strict: bool = True):
        self.strict = strict
        self._cached_results: Dict[int, ValidationResult] = {}

    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate JSON structure"""
        cache_key = hash(str(data))
        
        if cache_key in self._cached_results:
            return self._cached_results[cache_key].is_valid
            
        result = self._validate_structure(data)
        self._cached_results[cache_key] = result
        return result.is_valid
    
    def _validate_structure(self, data: Dict[str, Any]) -> ValidationResult:
        """Internal validation logic"""
        if not isinstance(data, dict):
            return ValidationResult(False, "Root must be a dictionary")
            
        if not is_valid_json_structure(data):
            return ValidationResult(False, "Invalid JSON structure")
            
        return ValidationResult(True)
    
    def clear_cache(self) -> None:
        """Clear validation cache"""
        self._cached_results.clear()
