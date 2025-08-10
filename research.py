#!/usr/bin/env python3

import sys
import re

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <filename> <regex>")
        sys.exit(1)

    filename = sys.argv[1]
    pattern_str = sys.argv[2]

    # Read the file in binary mode
    with open(filename, "rb") as f:
        data = f.read()

    # Compile the pattern as bytes (using .encode()).
    # DOTALL allows '.' to match any character including newlines.
    pattern_bytes = pattern_str.encode()
    regex = re.compile(pattern_bytes, flags=re.DOTALL)

    # Find all matches
    matches = regex.findall(data)

    # Print each match found
    # Note that each 'match' is a bytes object
    for match in matches:
        print(match)

if __name__ == "__main__":
    main()