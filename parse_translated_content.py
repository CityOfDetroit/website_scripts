#!/usr/bin/env python

import os
import sys

import json
import glob


class TranslatedContentParser():

    def parse_value(self, data, name):

        ret_val = ''

        val = data.get(name, {})
        if val:
            val = val[0]
            ret_val = val.get('value', '')

        return ret_val

    def parse_file(self, filename):
        """
        Parse an individual file.
        """

        with open(filename) as input:

            # get destination url
            url = input.readline().rstrip()
            print(url)

            # skip blank line
            input.readline()

            # now get the data
            data = input.readline()
            data = json.loads(data)

            title = self.parse_value(data, 'name')
            desc = self.parse_value(data, 'description')
            summary = self.parse_value(data, 'field_summary')

            self.output_file(url=url, title=title, desc=desc, summary=summary)

    def output_file(self, url, title, desc, summary):
        """
        Output the translated content.
        """

        self.output.write("\n" + url)
        self.output.write("\n")
        self.output.write("\ntitle:  " + title.rstrip())
        self.output.write("\ndescription:  " + desc.rstrip())
        self.output.write("\nsummary:   " + summary.rstrip())
        self.output.write("\n")
        self.output.write('\n*******************************************************************************\n')

    def parse(self, argv):
        """
        Parse all translated files in a given directory / language.
        """

        directory = sys.argv[1]
        lang = sys.argv[2]

        self.output = open(lang + "_content.txt", newline='', mode='wt', encoding='utf-8')

        for filename in glob.glob(directory + "/*.txt"):

            self.parse_file(filename)


if __name__ == '__main__':

    if len(sys.argv) is not 3:
        raise Exception("Usage:  <directory> <language>")

    TranslatedContentParser().parse(sys.argv)
