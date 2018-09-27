#!/usr/bin/env python

import sys

from google.cloud import translate


from parse_translated_content import TranslatedPage
from export_translations import ContentExporter

# from translations_loader import TranslationsLoader


import pdb


if __name__ == '__main__':


    pdb.set_trace()


    if len(sys.argv) != 2:
        raise Exception("Usage:  <url>")

    url = sys.argv[2]

    # First extract the english content to be translated
    true_url, data = ContentExporter.do_export(url=url, write_to_file=False)

    GOOGLE_APPLICATION_CREDENTIALS="[PATH]"

    # Instantiates a client
    translate_client = translate.Client()

    # The text to translate
    text = 'Hello, world!'

    target = 'es'

    # Translates some text into Russian
    translation = translate_client.translate(text, source_language='en', target_language=target)

    print(u'Text: {}'.format(text))
    print(u'Translation: {}'.format(translation['translatedText']))
