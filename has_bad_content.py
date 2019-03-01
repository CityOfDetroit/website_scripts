#!/usr/bin/env python

import os
import re
import sys


if __name__ == '__main__':

    if len(sys.argv) != 2:
        raise Exception("Usage:  has_bad_content.py <file name>")

    PATTERNS = {
        r'http[s]?\:\/[a-zA-Z]': "Invalid http / https protocol",
        r'detroitmi.theneighborhoods.org': "Invalid domain: detroitmi.theneighborhoods.org",
        r'detroitmi.prod.acquia-sites.com': "Invalid domain: detroitmi.prod.acquia-sites.com",
    }

    filename = sys.argv[1]
    with open(filename) as file:
        contents = file.read()

        pos = contents.find("\n")
        if pos > 0:
            contents = contents[pos + 2 : ]

        errors = []

        for pattern, description in PATTERNS.items():

            match = re.search(pattern, contents)
            if match:
                errors.append(description)

        if errors:
            print("File {} contains the following errors:  {}".format(filename, ', '.join(errors)))
            exit(code=1)
        else:
            exit(code=0)
