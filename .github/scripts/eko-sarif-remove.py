import json
import sys
import os
import tempfile
import shutil

def remove_duplicates(sarif_file):
    try:
        # Read the original file
        with open(sarif_file, 'r') as file:
            data = json.load(file)

        # Process the data
        rules = data['runs'][0]['tool']['driver']['rules']
        unique_rules = {rule['id']: rule for rule in rules}.values()
        data['runs'][0]['tool']['driver']['rules'] = list(unique_rules)

        # Write to a temporary file first
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.sarif') as temp_file:
            json.dump(data, temp_file, indent=2)
            temp_file_path = temp_file.name

        # Replace the original file
        shutil.move(temp_file_path, sarif_file)
        
        print(f"Successfully processed {sarif_file}")
        
    except PermissionError as e:
        print(f"Permission error: {e}")
        print("Try changing file permissions or running with appropriate privileges")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python remove.py <sarif_file>")
        sys.exit(1)
    remove_duplicates(sys.argv[1])