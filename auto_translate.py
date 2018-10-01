#!/usr/bin/env python

import sys

from google.cloud import translate


from parse_translated_content import TranslatedPage
from export_translations import ContentExporter

import load_translation

import inspect


def machine_translate(client, lang, text):

    # Translate the content
    translation = client.translate(text, source_language='en', target_language=lang)

    # print(translation['translatedText'])

    return translation['translatedText']


if __name__ == '__main__':

    if len(sys.argv) != 2:
        raise Exception("Usage:  <url>")

    url = sys.argv[1]

    if url.startswith('http'):
        url = url[7 : ]

        pos = url.find('/')
        url = url[pos : ]

    # Extract the content to be translated
    tmp = ContentExporter.do_export(url=url, write_to_file=False)
    if not tmp:

        ContentExporter.output_errs = True
        ContentExporter.do_export(url=url, write_to_file=False)
        ContentExporter.report_err_cnt()
        raise Exception('content could not be exported')

    true_url, data = tmp

    # Instantiate a translation client
    client = translate.Client.from_service_account_json('google_translate_key.json')

    source_page = TranslatedPage()
    source_page.parse_json(data)

    for lang in sorted(TranslatedPage.LANG_MAP.keys()):

        # Translate the content
        translated_page = TranslatedPage()

        translated_page.vid = source_page.vid
        translated_page.tid = source_page.tid

        translated_page.content = machine_translate(client=client, lang=lang, text=source_page.content)
        translated_page.title =machine_translate(client=client, lang=lang, text=source_page.title)
        translated_page.desc = machine_translate(client=client, lang=lang, text=source_page.desc)
        translated_page.organization_head_information = machine_translate(client=client, lang=lang, text=source_page.organization_head_information)
        translated_page.summary = machine_translate(client=client, lang=lang, text=source_page.summary)

        # Now write the translated content
        load_translation.Loader().run_page(lang, translated_page)
 
    print('\nLoaded all translations')
