#!/usr/bin/env python3
import sys
import os
import gzip
import io
from zipfile import BadZipFile, ZipFile
import xxtea
import jsbeautifier

# You can change these keys as needed:
KEY_XOR = "jycrypt"
KEY_XXTEA = "65485d8a-8161-4c"

def main():
    if len(sys.argv) < 2:
        print("Usage: python decrypt.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    # Read the entire input file as bytes
    with open(input_file, 'rb') as f:
        data = f.read()

    # XOR step with KEY_XOR
    key_bytes = KEY_XOR.encode('utf-8')
    key_len = len(key_bytes)
    xored_data = bytearray(len(data))
    for i in range(len(data)):
        xored_data[i] = data[i] ^ key_bytes[i % key_len]

    # Remove the first 7 bytes after XOR
    if len(xored_data) < 7:
        print("Error: XORed data is too short to remove 7 bytes.")
        sys.exit(1)
    xored_data = xored_data[7:]

    # XXTEA decrypt
    decrypted_data = xxtea.decrypt(xored_data, KEY_XXTEA)
    if not decrypted_data:
        print("Error: XXTEA decryption failed. Possibly a wrong key?")
        sys.exit(1)

    # Attempt GZIP decompression
    is_gzip_file = True
    try:
        final_data = gzip.decompress(decrypted_data)
        print("It IS a GZIP archive.")
    except gzip.BadGzipFile:
        print("It's NOT a GZIP archive.")
        is_gzip_file = False
        final_data = decrypted_data

    # Construct the output filename
    # (take the input filename without extension, add .js or .zip accordingly)
    base_name = os.path.splitext(input_file)[0]

    if not is_gzip_file:
        # Check if it's a ZIP archive
        try:
            zip_file = io.BytesIO(final_data)
            with ZipFile(zip_file) as _:
                pass  # If this succeeds, it's a valid ZIP
            output_file = base_name + ".zip"
            print("It IS a ZIP archive.")
        except BadZipFile:
            output_file = base_name + ".js"
            print("It is NOT a ZIP archive.")
    else:
        output_file = base_name + ".js"

    # If the output is a JS file, try to beautify it
    if output_file.endswith(".js"):
        try:
            # Attempt to decode final data as UTF-8
            decoded_str = final_data.decode("utf-8")
            # Beautify the JS code
            beautified_str = jsbeautifier.beautify(decoded_str)
            final_data = beautified_str.encode("utf-8")
        except UnicodeDecodeError:
            print("Warning: Could not decode final data as UTF-8. Skipping beautification.")

    # Write final data
    with open(output_file, 'wb') as out_f:
        out_f.write(final_data)

    print(f"Decrypted file written to: {output_file}")

if __name__ == "__main__":
    main()