#!/usr/bin/env python

import sys
import time

from google.cloud import translate

from parse_translated_content import TranslatedPage


class MachineTranslator():
    """
    Class for handling interaction with google translation api.
    """

    # Google translate api barfs if text is too long
    MAX_TEXT_LEN = 5000

    def __init__(self):
        """
        Set up the api.
        """

        # Instantiate a translation client
        self.client = translate.Client.from_service_account_json('google_translate_key.json')

    def translate_internal(self, lang, text):
        """
        Handle the call to the translation api.
        """

        # Translate the content
        translation = self.client.translate(text, source_language='en', target_language=lang)

        # Sleep 1 second to make sure we don't call google translate too often per second
        time.sleep(1)

        # print(translation['translatedText'])

        return translation['translatedText']

    def translate_chunks(self, lang, text):
        """
        Parse html into chunks that are short enough to translate.
        """

        translated_text = ''
        soup = BeautifulSoup(text, 'html.parser')

        for elt in soup.find_all('p'):

            tmp = self.translate_internal(lang, str(elt))
            translated_text += tmp + '\n'

        return translated_text

    def translate(self, lang, text):
        """
        Translate text to desired language.
        """

        if not text:
            return text

        if len(text) >= self.MAX_TEXT_LEN:

            return self.translate_chunks(lang, text)

        else:

            return self.translate_internal(lang, text)


if __name__ == '__main__':

    # Translate a file into all desired languages.

    # Usage:  machine_translator.py <file>
    #  e.g.,  machine_translator.py 'crio.txt'

    if len(sys.argv) != 2:
        raise Exception("Usage:  filename")

    with open(sys.argv[1]) as file_in:

        content = file_in.read()
        translator = MachineTranslator()

        for lang in sorted(TranslatedPage.LANG_MAP.keys()):

            output = translator.translate(lang, content)
            with open(f"{lang}_" + filename, "w") as file_out:

                file_out.write(output)

    print('\nSaved all translations\n')
