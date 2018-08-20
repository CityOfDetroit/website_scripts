#!/usr/bin/env python

import os
import sys

import json
import glob


class TranslatedContentParser():

    def parse_file(self, filename):
        """
        Parse an individual file.
        """

        print(filename)

        with open(filename) as input:

            # get destination url
            url = input.readline().rstrip()
            print(url)

            # skip blank line
            input.readline()

            # now get the data
            data = input.readline()
            data = json.loads(data)

            title = data['name'][0]['value']
            desc = data['description'][0]['value']
            summary = data['field_summary'][0]['value']

            self.output_file(title=title, desc=desc, summary=summary)

    def output_file(self, title, desc, summary):
        """
        Output the translated content.
        """

        print("\ntitle:  " + title.rstrip())
        print("\ndescription:  " + desc.rstrip())
        print("\nsummary:   " + summary.rstrip())
        print("\n")

    def parse(self, argv):
        """
        Parse all translated files in a given directory / language.
        """

        directory = sys.argv[1]
        lang = sys.argv[2]

        for filename in glob.glob(directory + "/*.txt"):

            self.parse_file(filename)


if __name__ == '__main__':

    if len(sys.argv) is not 3:
        raise Exception("Usage:  <directory> <language>")

    TranslatedContentParser().parse(sys.argv)
