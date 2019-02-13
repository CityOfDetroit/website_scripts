#!/usr/bin/env python

import re
import sys


def usage():
    raise Exception("Usage:  input_file remove_old_nums=[yes|no]")

if __name__ == '__main__':

    if len(sys.argv) != 3:
        usage()

    file = open(sys.argv[1])
    remove_old_nums = open(sys.argv[2])

    if remove_old_nums not in ["yes", "no"]:
        usage()

    remove_old_nums = remove_old_nums == "yes"

    for line_num, line in enumerate(file):

        if remove_old_nums:
            pos = re.search(r'\,\d+', line)
            if not pos:
                print("Error: no line number found in line {}".format(line))
            else:
                line = line[pos.start() : ]

        print(line.strip() + "," + str(line_num))
