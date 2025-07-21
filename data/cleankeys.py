import json
import binascii
import os
import sys
import base64

# cleankeys.py input output: clean
# cleankeys.py input output base32: base32 encode all

def encode_key(key):
    if len(sys.argv) > 3 and sys.argv[3] == "base32":
        return base64.b16encode(key.encode('utf-8')).decode('utf-8')

    if ' ' in key or '-' in key:
        return base64.b64encode(key.encode('utf-8')).decode('utf-8')
    return key

def encode_keys_recursive(obj):
    if isinstance(obj, dict):
        return {
            encode_key(key): encode_keys_recursive(value)
            for key, value in obj.items()
        }
    elif isinstance(obj, list):
        return [encode_keys_recursive(item) for item in obj]
    else:
        return obj

def encode_selected_keys(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)

    if os.path.exists(output_file):
        print(f"Error: Output file '{output_file}' already exists.")
        sys.exit(1)

    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:

        for line in infile:
            line = line.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
                encoded_obj = encode_keys_recursive(obj)
                outfile.write(json.dumps(encoded_obj) + '\n')
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON line: {line}")
                continue

if __name__ == "__main__":
    input_path = os.path.abspath(sys.argv[1])
    output_path = os.path.abspath(sys.argv[2])
    encode_selected_keys(input_path, output_path)

