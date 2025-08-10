#!/usr/bin/env python3

import sys
import os
import io
import gzip
import xxtea
from jsmin import jsmin

# You can change these keys as needed:
KEY_XOR = "jycrypt"
KEY_XXTEA = "65485d8a-8161-4c"

def main():
    if len(sys.argv) < 2:
        print("Usage: python encrypt.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    # Read the entire input file (expected JS code)
    with open(input_file, 'rb') as f:
        data = f.read()

    # Convert to text (UTF-8) for JS minification
    # (If your file has a different encoding, adjust accordingly)
    try:
        text_data = data.decode('utf-8')
    except UnicodeDecodeError:
        print("Warning: Could not fully decode file as UTF-8. Proceeding with 'replace' errors policy.")
        text_data = data.decode('utf-8', errors='replace')

    # Minify using jsmin
    minified_text = jsmin(text_data)
    minified_data = minified_text.encode('utf-8')

    # GZIP compress the minified data
    gzip_buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=gzip_buffer, mode='wb') as gz:
        gz.write(minified_data)
    compressed_data = gzip_buffer.getvalue()

    # XXTEA encrypt the compressed data
    encrypted_data = xxtea.encrypt(compressed_data, KEY_XXTEA)

    # XOR with KEY_XOR
    key_bytes = KEY_XOR.encode('utf-8')
    key_len = len(key_bytes)
    xored_data = bytearray(len(encrypted_data))
    for i in range(len(encrypted_data)):
        xored_data[i] = encrypted_data[i] ^ key_bytes[i % key_len]

    # Construct output filename (same base name, .jsc extension)
    base_name = os.path.splitext(input_file)[0]
    output_file = base_name + ".jsc"

    # Write the "jycrypt" literal first, then the XOR'ed data
    with open(output_file, 'wb') as out_f:
        out_f.write(key_bytes)    # Write the 7 bytes of "jycrypt"
        out_f.write(xored_data)   # Then the encrypted (XXTEA) + XOR'ed data

    print(f"Encrypted file written to: {output_file}")

if __name__ == "__main__":
    main()