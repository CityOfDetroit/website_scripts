#!/usr/bin/env python

import sys

from google.cloud import translate


from parse_translated_content import TranslatedPage
from export_translations import ContentExporter

import load_translation

import inspect


import pdb


def machine_translate(client, lang, text):

    # Translate the content
    translation = client.translate(text, source_language='en', target_language=lang)

    print(translation['translatedText'])

    return translation['translatedText']


if __name__ == '__main__':

    if len(sys.argv) != 2:
        raise Exception("Usage:  <url>")

    url = sys.argv[1]

    # Extract the content to be translated
    true_url, data = ContentExporter.do_export(url=url, write_to_file=False)


    pdb.set_trace()


    # Instantiate a translation client
    client = translate.Client.from_service_account_json('google_translate_key.json')

    source_page = TranslatedPage()
    source_page.parse_json(data)

    lang = 'es'

    # Translate the content
    translated_page = TranslatedPage()

    translated_page.content = machine_translate(client=client, lang=lang, text=source_page.content)
    translated_page.title =machine_translate(client=client, lang=lang, text=source_page.title)
    translated_page.desc = machine_translate(client=client, lang=lang, text=source_page.desc)
    translated_page.organization_head_information = machine_translate(client=client, lang=lang, text=source_page.organization_head_information)
    translated_page.summary = machine_translate(client=client, lang=lang, text=source_page.summary)

    # Now write the translated content
    load_translation.Loader().run_page(lang, page)
