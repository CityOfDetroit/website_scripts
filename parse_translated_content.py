#!/usr/bin/env python

import os
import sys

import json
import glob


import pdb


class TranslatedContentParser():

    def parse(self, argv):
        """
        Parse all translated files in a given directory / language.
        """


        # pdb.set_trace()


        directory = sys.argv[1]
        lang = sys.argv[2]

        for file in glob.glob(directory + "/*.txt"):
            print(file)

            with open(file) as input:

                # get destination url
                url = input.readline().rstrip()
                print(url)

                # skip blank line
                input.readline()

                # now get the data
                data = input.readline()
                data = json.loads(data)
                print(type(data))


if __name__ == '__main__':

    if len(sys.argv) is not 3:
        raise Exception("Usage:  <directory> <language>")

    TranslatedContentParser().parse(sys.argv)
