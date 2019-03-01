#!/usr/bin/env python

import os
import re
import sys


if __name__ == '__main__':

    if len(sys.argv) != 2:
        raise Exception("Usage:  has_bad_content.py <file name>")

    filename = sys.argv[1]
    with open(filename) as file:
        contents = file.read()

        match = re.search(r'http[s]?\:\/[a-zA-Z]', contents)

        code = 1 if match else 0
        exit(code=code)
