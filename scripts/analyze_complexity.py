import lizard
import json
import os
import argparse

def extract_function_metrics(file_path, function_name, output_json="data/lizard_metrics.json"):
    # Runs Lizard analysis on a given file and extracts metrics for a specific function.
    # Saves the extracted data in JSON format.

    # Run Lizard analysis on the file
    analysis = lizard.analyze_file(file_path)

    # Extract function metrics
    function_data = None
    for function in analysis.function_list:
        if function.name == function_name:
            function_data = {
                "lines_of_code": function.length,  # Total LOC
                "number_of_parameters": function.parameter_count,  # Parameters
                "cyclomatic_complexity": function.cyclomatic_complexity,  # Cyclomatic Complexity
                "logical_lines_of_code": function.nloc,  # LLOC
                "function": function_name,
                "file": file_path,
                "start_line": function.start_line,
                "end_line": function.end_line
            }
            break  # Stop searching once we find the function

    # If the function isn't found, return an error message
    if function_data is None:
        print(f"Function '{function_name}' not found in '{file_path}'")
        return

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_json), exist_ok=True)

    # Save to JSON file (overwrite on each run)
    with open(output_json, "w") as json_file:
        json.dump(function_data, json_file, indent=4)

    print(f"Metrics for '{function_name}' saved to {output_json}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract Lizard metrics for a specific function and save as JSON")
    parser.add_argument("file", help="Path to the Python file")
    parser.add_argument("function", help="Function name to analyze")
    parser.add_argument("--output", default="data/lizard_metrics.json", help="Path to output JSON file")
    args = parser.parse_args()

    extract_function_metrics(args.file, args.function, args.output)
