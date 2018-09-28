#!/usr/bin/env python

import sys

from google.cloud import translate


from parse_translated_content import TranslatedPage
from export_translations import ContentExporter

# from translations_loader import TranslationsLoader

import inspect


import pdb


if __name__ == '__main__':

    if len(sys.argv) != 2:
        raise Exception("Usage:  <url>")

    url = sys.argv[1]

    # Extract the content to be translated
    true_url, data = ContentExporter.do_export(url=url, write_to_file=False)


    pdb.set_trace()


    # Instantiate a translation client
    client = translate.Client.from_service_account_json('google_translate_key.json')

    page = TranslatedPage()
    page.parse_json(data)

    for value in [ page.content, page.title, page.desc, page.organization_head_information, page.faq, page.summary ]:

        if value:

            for lang in TranslatedPage.LANG_MAP.keys():

                # Translate the content
                translation = client.translate(value, source_language='en', target_language=lang)

                print(translation['translatedText'])
