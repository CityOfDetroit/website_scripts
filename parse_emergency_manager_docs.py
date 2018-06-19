#!/usr/bin/env python

import os
import json
from json import JSONEncoder
from json import JSONDecoder
import re
import sys


class EMDocsParser():

    DATA_TAGS = ('a', 'div')

    def __init__(self):

        self.category = 'Emergency Manager Orders'
        self.sub_category = ''
        self.grab_category = False

    def get_first_tag(line):
        """
        Returns the tag for this line.
        """

        match = re.search('<', line)

        # In case line has no tags.
        if not match:
            return '', ''

        line = line[match.start() + 1 : ]

        # find end of tag
        match = re.search('[ >]', line)
        if not match:
            return '', ''

        return line[0 : match.start()], line

    def parse_value(line, str_begin, str_end='\"'):

        begin = line.find(str_begin)
        if begin < 0:
            return line, None

        begin = begin + len(str_begin)

        end = line.find(str_end, begin)
        if end < 0:
            return line, None

        value = line[begin : end].strip()
        line = line[end + len(str_end) : ]

        return line, value

    def parse_line(self, tag, line):
        """
        Retrieve relevant content from line.
        """

        if tag == 'a':

            new_line, title = EMDocsParser.parse_value(line=line, str_begin=' title=\"')
            new_line, url = EMDocsParser.parse_value(line=line, str_begin=' href=\"')

            url = url.replace("/Portals/0/docs/EM/", "")
            line = new_line

            if not title or not url:
                return None

            return { title : url }

        elif tag == 'div':

            line, class_val = EMDocsParser.parse_value(line=line, str_begin=' class=\"')
            if class_val and "dt-faq-item" in class_val:
                self.grab_category = True

        return None

    def get_sub_category(self, line):

        begin = line.find('<h3>') + 4
        end = line.find('</h3>', begin)

        self.sub_category = line[begin : end].strip()

    def parse(self, filename):

        filename = sys.argv[1]
        with open(filename, newline='', encoding="utf8") as input_file:

            content = {}
            for line in input_file:

                if self.category == 'Emergency Manager Reports' and '<h3>' in line:

                    self.get_sub_category(line)
                    line = ''

                while line:

                    if self.grab_category:

                        self.category = line.strip()
                        self.grab_category = False

                    tag, line = EMDocsParser.get_first_tag(line)
                    if tag in EMDocsParser.DATA_TAGS:

                        line_info = self.parse_line(tag, line)
                        if line_info:

                            if self.category == 'Emergency Manager Reports':

                                if not content.get(self.category):
                                    content[self.category] = {}

                                if not content[self.category].get(self.sub_category):
                                    content[self.category][self.sub_category] = []

                                content[self.category][self.sub_category].append(line_info)

                            else:

                                if not content.get(self.category):
                                    content[self.category] = []

                                content[self.category].append(line_info)

                        elif self.grab_category:

                            line = ''

            data = {
                "base_path": "/files/emergency_manager_docs/",
                "reports": content
            }

            print(json.dumps(data))


if __name__ == "__main__":

    if len(sys.argv) < 2:
        msg = "usage:  {} input_file\n(e.g., {} website_data/emergency_manager_orders/content.html".format(sys.argv[0], sys.argv[0])
        raise Exception(msg)

    EMDocsParser().parse(sys.argv[1])
