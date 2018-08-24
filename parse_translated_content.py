#!/usr/bin/env python

import os
import sys

import json
import glob


class TranslatedPage():

    CLEANUPS = {
        "&lt;": "<",
        "&gt;": ">",
    }

    LANG_MAP = {
        "ar": "arabic",
        "bn": "bengali",
        "es": "spanish",
    }

    def clean_value(self, value):

        for bad, good in self.CLEANUPS.items():
            value = value.replace(bad, good)

        return value

    def parse_value(self, data, name):

        ret_val = ''

        val = data.get(name, {})
        if val:
            val = val[0]
            ret_val = val.get('value', '')

        return self.clean_value(ret_val)

    def parse_file(self, filename):
        """
        Parse an individual file.
        """

        with open(filename) as input:

            # get destination url
            self.url = input.readline().rstrip()
            print(self.url)

            # skip blank line
            input.readline()

            # now get the data
            data = input.readline()
            data = json.loads(data)

            self.title = self.parse_value(data, 'name')
            self.desc = self.parse_value(data, 'description')
            self.summary = self.parse_value(data, 'field_summary')

    def output_file(self, url, lang):
        """
        Output the translated content.
        """

        self.output.write("\n" + "language: " + self.LANG_MAP[lang])
        self.output.write("\n" + url)
        self.output.write("\n")
        self.output.write("\ntitle:  " + self.title.rstrip())
        self.output.write("\ndescription:  " + self.desc.rstrip())
        self.output.write("\nsummary:   " + self.summary.rstrip())
        self.output.write("\n")
        self.output.write('\n*******************************************************************************\n')


class TranslatedContentParser():

    translations = {
        "ar": {},
        "bn": {},
        "es": {},
    }

    def parse_files(self):

        for lang, directory in self.content.items():

            for filename in glob.glob(directory + "/*.txt"):

                page = TranslatedPage()
                page.parse_file(filename)

                self.translations[lang][page.url] = page

    def output(self):

        for url in list(ar_content.translations.keys()):

            for lang, page in self.content.items():

                page.output_file(url=self.url, lang=lang)

    def parse(self, argv):
        """
        Parse all translated files in a given directory / language.
        """

        self.content = {
            "ar" : sys.argv[1],
            "bn" : sys.argv[2],
            "es" : sys.argv[3],
        }

        self.output = open("transltated_content.txt", newline='', mode='wt', encoding='utf-8')

        self.parse_files()

        self.output()


if __name__ == '__main__':

    if len(sys.argv) is not 4:
        raise Exception("Usage:  <ar directory> <bn directory> <es directory>")

    TranslatedContentParser().parse(sys.argv)
