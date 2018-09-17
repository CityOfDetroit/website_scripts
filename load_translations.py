#!/usr/bin/env python

from parse_translated_content import TranslatedPage
from translations_loader import TranslationsLoader


if __name__ == '__main__':

    loader = TranslationsLoader()

    loader.start()

    # loader.table_names()

    page = TranslatedPage()
    filename = "translated_content/es/%2Fdepartments%2Fdetroit-fire-department%2Ffire-investigation-division%2Farson-awareness9.txt"
    lang = 'es'
    page.parse_file(filename=filename)

    loader.load_page(page=page, lang=lang)
    loader.check_page(page=page, lang=lang)

    loader.stop()
