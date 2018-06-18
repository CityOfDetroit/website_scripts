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


class TranslationsDecoder():

    def __init__(self, filename, output):

        self.filename = filename
        self.output = output

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

                self.output.write("\nurl:  " + self.url)
                self.output.write("\ntitle:  " + title)
                self.output.write("\ndescription:  " + description)
                self.output.write("\nsummary:   " + summary)

                self.output.write('\n\n*******************************************************************************\n')

    def decode_line(self, line):

        if re.match('^url\: ', line):

            self.report()
            self.url = TranslationsDecoder.get_url(line)

        else:

            if line.rstrip():
                self.content = line.rstrip()

    def decode(self):

        with open(self.filename, newline='', encoding='utf-8') as file:

            with open(self.output, newline='', mode='wt', encoding='utf-8') as self.output:

                self.url = ''
                self.content = ''
                line_cnt = 0

                for line in file:

                    line_cnt = line_cnt + 1
                    self.decode_line(line)

                self.report()

        print("read {} lines".format(line_cnt))


if __name__ == '__main__':

    if len(sys.argv) < 3:
        raise Exception("usage:  parse_translations.py <input file> <output file>")

    filename = sys.argv[1]
    output = sys.argv[2]
    TranslationsDecoder(filename=filename, output=output).decode()
