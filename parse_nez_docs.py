#!/usr/bin/env python

from os import listdir
from os.path import isfile, join
import re
import sys


import pdb


PATTERNS = [
    r'JCC',
    r'Hearing',
    r'Assessor',
    r'Resolution',
    r'Petition',
    r'PDD',
    r'Clerk',
]

def find_first_pattern(file):

    for pattern in PATTERNS:
        match = re.search(pattern, file)
        if match:
            return match

    return None

def get_title(file, match):

    title = file[0 : match.end()]
    title = title.replace('_', ' ')
    # print(file + "    -    " + title)
    return title

def get_year(title):

    OFFSET = 4
    match = re.search(r'[\d]{4}', title[OFFSET : ])
    if not match:
        return None

    year = title[match.start() + OFFSET : match.end() + OFFSET]
    return int(year)


if __name__ == '__main__':

    if len(sys.argv) != 2:
        msg = "usage:  ./parse_nez_docs.py <path to nez docs"
        raise Exception(msg)

    script_file = sys.argv[0][2:]
    path = sys.argv[1]

    files = [ file for file in listdir(path) if isfile(join(path, file)) and file != script_file ]

    print("URL,Title,Year")

    for file in files:

        match = find_first_pattern(file)
        if not match:
            raise Exception(msg="File name {} could not be parsed".format(file))

        title = get_title(file, match)
        year = get_year(title)
        print("\"{}\",\"{}\",{}".format("https://detroitmi.gov/sites/detroitmi.localhost/files/migrated_docs/nez_reports/" + file, title, year))
