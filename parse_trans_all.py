#!/usr/bin/env python

import os
import re
import sys


replacements = [
    ('\'', '"'),
    ("\\n", " "),
    ("\\r", ""),
    ("\\t", "  "),
]


class Page():

    def __init__(self, title, description, summary=None):

        self.title = title
        self.description = description
        self.summary = summary

    def start_urL(url):

        file.write("\nurl:  " + url)
        file.write("\n")

    def write(self, file):

        file.write("\ntitle:  " + self.title.rstrip())
        file.write("\ndescription:  " + self.description.rstrip())
        file.write("\nsummary:   " + self.summary.rstrip())
        file.write("\n")

    def end_urL(url):

        file.write('\n*******************************************************************************\n')


class TranslationsDecoder():

    def __init__(self, input):

        self.input = input
        self.translations = {}

    def get_url(line):
        return line.rstrip()[5 : ]

    def cleanup_val(val):

        for replacement in replacements:
            val = val.replace(replacement[0], replacement[1])

        return val

    def parse_val(content, BEGIN_STR, END_STR, default='Not Available'):

        begin = content.find(BEGIN_STR)
        if begin >= 0:
            end = content.find(END_STR, begin)
        else:
            return default

        val = content[begin + len(BEGIN_STR) : end]
        return TranslationsDecoder.cleanup_val(val)

    def get_title(content):

        BEGIN_STR = "'name': [{'value': '"
        END_STR = "'}],"

        return TranslationsDecoder.parse_val(content, BEGIN_STR, END_STR)

    def get_description(content):

        BEGIN_STR = "'description': [{'value': '"
        END_STR = "', 'format': 'full_html'"

        return TranslationsDecoder.parse_val(content, BEGIN_STR, END_STR)

    def get_summary(content):

        BEGIN_STR = "'field_summary': [{'value': '"
        END_STR = "', 'format': "

        return TranslationsDecoder.parse_val(content, BEGIN_STR, END_STR)

    def report(self):

        if self.url and self.content:

            title = TranslationsDecoder.get_title(self.content)
            description = TranslationsDecoder.get_description(self.content)
            summary = TranslationsDecoder.get_summary(self.content)
            if title and description:

                page = Page(title=title, description=description, summary=summary)
                self.translations[self.url] = page

    def decode_line(self, line):

        if re.match('^url\: ', line):

            self.report()
            self.url = TranslationsDecoder.get_url(line)

        else:

            if line.rstrip():
                self.content = line.rstrip()

    def decode(self):

        with open(self.input, newline='', encoding='utf-8') as file:

            self.url = ''
            self.content = ''
            line_cnt = 0

            for line in file:

                line_cnt = line_cnt + 1
                self.decode_line(line)

            self.report()


if __name__ == '__main__':

    if len(sys.argv) < 5:
        raise Exception("""
            usage:  parse_translations.py <ar input> <bn input> <es input> <output file>
            e.g., ./parse_trans_all.py translations/ar/translations.txt translations/bn/translations.txt translations/es/translations.txt combined.txt""")

    inputs = {
        "ar": sys.argv[1],
        "bn": sys.argv[2],
        "es": sys.argv[3],
    }
    output = sys.argv[4]

    ar_content = TranslationsDecoder(input=inputs["ar"])
    ar_content.decode()

    bn_content = TranslationsDecoder(input=inputs["bn"])
    bn_content.decode()

    es_content = TranslationsDecoder(input=inputs["es"])
    es_content.decode()

    translations = {
        "ar": ar_content.translations,
        "bn": bn_content.translations,
        "es": es_content.translations,
    }

    with open(output, newline='', mode='wt', encoding='utf-8') as file:

        for url in list(ar_content.translations.keys()):

            Page.start_urL(url)

            for language, translation in translations.items():

                page = translation.get(url)
                if page:
                    page.write(file)
                else:
                    print("no translation available in {} for {}".format(language, url))

            Page.end_urL(url)