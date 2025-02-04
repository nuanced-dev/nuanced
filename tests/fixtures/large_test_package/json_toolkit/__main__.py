import sys
from typing import Optional
import argparse

from .core.parser import Parser
from .core.transformer import transform_nested
from .utils.io import read_json_file, write_json_file

def main(input_file: Optional[str] = None, output_file: Optional[str] = None) -> int:
    parser = argparse.ArgumentParser(description='JSON Transformation Tool')
    parser.add_argument('--input', default=input_file, help='Input JSON file')
    parser.add_argument('--output', default=output_file, help='Output JSON file')
    args = parser.parse_args()

    if not args.input:
        print("Error: Input file required")
        return 1

    try:
        data = read_json_file(args.input)
        json_parser = Parser()
        
        if not json_parser.validate(data):
            print("Error: Invalid JSON structure")
            return 1
            
        transformed = transform_nested(data)
        
        if args.output:
            write_json_file(transformed, args.output)
        else:
            print(transformed)
            
        return 0
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

# Run if script is executed directly
if __name__ == "__main__":
    sys.exit(main())
