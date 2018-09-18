#!/usr/bin/env python

import os
import sys

import json
import glob
import requests

from export_translations import ContentExporter


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

    def __init__(self):


        self.url = ''
        self.content = ''
        self.title = ''
        self.desc = ''
        self.organization_head_information = ''
        self.faq = []
        self.summary = ''

    def clean_value(self, value):

        if not value:
            return ''

        if type(value) is not str:
            return value

        for bad, good in self.CLEANUPS.items():
            value = value.replace(bad, good)

        return value.strip()

    def parse_value(self, data, name, val_name='value', alt_name=''):

        ret_val = ''

        val = data.get(name, {})
        if val:
            val = val[0]
            ret_val = val.get(val_name, '')
        elif alt_name:
            return self.parse_value(data=data, name=alt_name, val_name=val_name)

        return self.clean_value(ret_val)

    def parse_json(self, data):
        """
        Parse json object.
        """

        self.tid = self.parse_value(data=data, name='tid')
        self.vid = self.parse_value(data=data, name='vid', val_name='target_id')

        self.title = self.parse_value(data=data, name='name', alt_name='title')
        self.desc = self.parse_value(data=data, name='description')
        self.organization_head_information = self.parse_value(data=data, name='field_organization_head_informat')

        faq_pairs = data.get('field_faq_pair', [])
        for faq_pair in faq_pairs:

            content = faq_pair.get('content', [])
            self.faq.extend(content)

        self.summary = self.parse_value(data=data, name='field_summary')

        self.content = ''

    def parse_homepage(self, input):
        """
        Parse homepage.
        """

        self.url = "detroitmi.theneighborhoods.org"
        self.content = input.read()

    def parse_file(self, filename):
        """
        Parse an individual file.
        """

        with open(filename, mode="r", encoding="utf-8-sig") as input:

            # get destination url
            self.url = input.readline().rstrip()
            if self.url.startswith('<'):
                self.parse_homepage(input)
                return

            pos = self.url.find('?')
            if pos > 0:
                self.url = self.url[:pos]

            print(self.url)

            # skip blank line
            input.readline()

            # now get the data
            data = input.readline()
            data = json.loads(data)

            self.parse_json(data)

    def output_file(self, output, url, lang):
        """
        Output the translated content.
        """

        output.write("\n" + "language: " + self.LANG_MAP[lang])
        output.write("\n" + url)
        output.write("\n")

        if self.content:
            output.write("\ncontent:\n" + self.content.rstrip() + "\n")

        output.write("\ntitle:  " + self.title.rstrip())
        output.write("\ndescription:  " + self.desc.rstrip())
        output.write("\norganization information:  " + self.organization_head_information.rstrip())

        if self.faq:
            output.write("\nfaq:\n")
            for faq_pair in self.faq:
                output.write("\nquestion:  " + faq_pair['question'])
                output.write("\nanswer:  " + faq_pair['answer'])

        output.write("\nsummary:   " + self.summary.rstrip())
        output.write("\n")
        output.write('\n*******************************************************************************\n')

    def compare(self, other):
        """
        Compares self with other TranslatedPage and returns differences.
        """

        differences = []
        for attr in [ 'title', 'desc', 'organization_head_information', 'summary' ]:

            if getattr(self, attr) != getattr(other, attr):
                differences.append(attr)

        return differences


class TranslatedContentParser():

    translations = {
        "ar": {},
        "bn": {},
        "es": {},
    }

    def get_urls(self):

        urls = list(self.translations["ar"].keys()) + list(self.translations["bn"].keys()) + list(self.translations["es"].keys())
        return sorted(set(urls))

    def get_langs(self):

        return sorted(self.translations.keys())

    def parse_files(self):
        """
        Parse content from language line.
        """

        for lang, directory in self.content.items():

            for filename in glob.glob(directory + "/*.txt"):

                page = TranslatedPage()
                page.parse_file(filename)

                self.translations[lang][page.url] = page

    def output_content(self):
        """
        Output all the translated content, sorted by url and language.
        """

        for url in self.get_urls():

            for lang in self.get_langs():

                page = self.translations[lang].get(url)
                if page:
                    page.output_file(output=self.output, url=url, lang=lang)

    def check_content(self):
        """
        Report any content not-yet loaded or loaded incorrectly.
        """

        for url in self.get_urls():

            original_url = url

            url = url.replace('http://', '')
            url = url.replace('https://', '')
            pos = url.find('/')
            url = url[pos:]

            junk_url, data = ContentExporter.get_data(url)

            if not data.get('tid'):
                continue

            tid = data['tid'][0]['value']
            base_url = '/taxonomy/term/{}'.format(tid)

            for lang in self.get_langs():

                translated_page = self.translations[lang].get(original_url)
                if not translated_page:
                    continue

                translated_url, data = ContentExporter.get_data('/' + lang + base_url)

                loaded_page = TranslatedPage()
                loaded_page.parse_json(data)

                differences = translated_page.compare(loaded_page)

                if differences:

                    print("{} - {} ({})".format(lang, original_url, str(differences)[1:-1]))


    def parse(self, argv):
        """
        Parse all translated files in a given directory / language.
        """

        self.content = {
            "ar" : sys.argv[1],
            "bn" : sys.argv[2],
            "es" : sys.argv[3],
        }

        check_loaded_content = False
        if len(sys.argv) == 5:
            check_loaded_content = (sys.argv[4] == 'check_content=y')

        self.output = open("translated_content.txt", newline='', mode='wt', encoding='utf-8')

        self.parse_files()

        if check_loaded_content:
            self.check_content()
        else:
            self.output_content()


if __name__ == '__main__':

    if len(sys.argv) not in (4,5):
        raise Exception("Usage:  <ar directory> <bn directory> <es directory> [check_loaded_content=y|n]")

    TranslatedContentParser().parse(sys.argv)
