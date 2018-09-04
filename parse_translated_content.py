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

        if not value:
            return ''

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

        with open(filename, mode="r", encoding="utf-8-sig") as input:

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
            self.organization_head_information = self.parse_value(data, 'field_organization_head_informat')
            self.summary = self.parse_value(data, 'field_summary')

    def output_file(self, output, url, lang):
        """
        Output the translated content.
        """

        output.write("\n" + "language: " + self.LANG_MAP[lang])
        output.write("\n" + url)
        output.write("\n")
        output.write("\ntitle:  " + self.title.rstrip())
        output.write("\ndescription:  " + self.desc.rstrip())
        output.write("\norganization information:  " + self.organization_head_information.rstrip())
        output.write("\nsummary:   " + self.summary.rstrip())
        output.write("\n")
        output.write('\n*******************************************************************************\n')


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

    def output_content(self):

        for url in sorted(self.translations["ar"].keys()):

            for lang in sorted(self.translations.keys()):

                page = self.translations[lang].get(url)
                if page:
                    page.output_file(output=self.output, url=url, lang=lang)


    def parse(self, argv):
        """
        Parse all translated files in a given directory / language.
        """

        self.content = {
            "ar" : sys.argv[1],
            "bn" : sys.argv[2],
            "es" : sys.argv[3],
        }

        self.output = open("translated_content.txt", newline='', mode='wt', encoding='utf-8')

        self.parse_files()

        self.output_content()


if __name__ == '__main__':

    if len(sys.argv) is not 4:
        raise Exception("Usage:  <ar directory> <bn directory> <es directory>")

    TranslatedContentParser().parse(sys.argv)
