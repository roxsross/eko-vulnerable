import json
import sys

def remove_duplicates(sarif_file):
    with open(sarif_file, 'r') as file:
        data = json.load(file)

    rules = data['runs'][0]['tool']['driver']['rules']
    unique_rules = {rule['id']: rule for rule in rules}.values()
    data['runs'][0]['tool']['driver']['rules'] = list(unique_rules)

    with open(sarif_file, 'w') as file:
        json.dump(data, file, indent=2)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python remove.py <sarif_file>")
        sys.exit(1)
    remove_duplicates(sys.argv[1])