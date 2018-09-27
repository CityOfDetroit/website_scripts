#!/usr/bin/env python

import sys

from parse_translated_content import TranslatedPage
from translations_loader import TranslationsLoader


import pdb


class Loader():

    def run(lang, filename):


        pdb.set_trace()


        if '/' + lang + '/' not in filename:
            raise Exception("Error:  lang {} appears wrong based on file path".format(lang))

        loader = TranslationsLoader()

        loader.start()

        page = TranslatedPage()

        try:
            page.parse_file(filename=filename)

            loader.load_page(page=page, lang=lang)
            loader.check_page(page=page, lang=lang)

        except Exception as exc:
            print("Exception caught: " + str(exc))

        loader.stop()


if __name__ == '__main__':

    # Usage:  <language> <filename>
    # e.g., load_translation.py es translated_content/es/%2Fdepartments%2Fdetroit-fire-department%2Ffire-investigation-division%2Farson-awareness9.txt

    if len(sys.argv) != 3:
        raise Exception("Usage:  <language> <filename>")

    lang = sys.argv[1]
    filename = sys.argv[2]

    Loader().run(lang=lang, filename=filename)
