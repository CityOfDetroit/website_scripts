#!/usr/bin/env python

import sys

from parse_translated_content import TranslatedPage
from translations_loader import TranslationsLoader


if __name__ == '__main__':

    # Usage:  <language> <filename>
    # e.g., load_translations.py es translated_content/es/%2Fdepartments%2Fdetroit-fire-department%2Ffire-investigation-division%2Farson-awareness9.txt

    if len(sys.argv) != 3:
        raise Exception("Usage:  <language> <filename>")

    lang = sys.argv[1]
    filename = sys.argv[2]

    if '/' + lang + '/' not in filename:
        raise Exception("Error:  lang {} appears wrong based on file path".format(lang))

    loader = TranslationsLoader()

    loader.start()

    # loader.table_names()

    page = TranslatedPage()
    page.parse_file(filename=filename)

    loader.load_page(page=page, lang=lang)
    loader.check_page(page=page, lang=lang)

    loader.stop()
