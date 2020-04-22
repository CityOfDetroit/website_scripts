#!/usr/bin/env python

import os
import sys
import time

from google.cloud import translate
from bs4 import BeautifulSoup


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

    def translate_elt(self, lang, elt):
        """
        Traverse the html and translate each tag that has content.
        """

        text = str(elt)
        output = ""

        if text == "\n":

            return "\n"

        # If the length of the tag is too long, then try recurring on the tag's children.
        elif len(text) > MachineTranslator.MAX_TEXT_LEN and elt.children:

            first_child_pos = text.find('<', len(elt.name) + 1)
            if first_child_pos > 0:

                output += text[ : first_child_pos]

            for tag in elt.children:

                output += self.translate_elt(lang=lang, elt=tag)

            output += "</" + elt.name + ">"

        else:

            # Translate this tag.
            output = self.translate_internal(lang=lang, text=text) + "\n"

        return output

    def translate(self, lang, text):
        """
        Translate text to desired language.
        """

        if not text:
            return ""

        soup = BeautifulSoup(text, 'html.parser')

        output = ""
        for tag in soup.children:

            output += self.translate_elt(lang=lang, elt=tag)

        return output


if __name__ == '__main__':

    # Translate a file into all desired languages.

    # Usage:  machine_translator.py <file>
    #  e.g.,  machine_translator.py 'crio.txt'

    if len(sys.argv) != 2:
        raise Exception("Usage:  filename")

    filename = sys.argv[1]
    dot_pos = filename.find('.')

    # Figure out our output file names and go ahead
    # and delete previous output files.
    filenames = {}
    for lang in TranslatedPage.LANG_MAP.keys():

        filename_out = f"{filename[ : dot_pos]}_{lang}.txt"
        filenames[lang] = filename_out

        try:

            os.remove(filename_out)

        except FileNotFoundError:

            pass

    # Now read the input and translate it.
    with open(filename) as file_in:

        content = file_in.read()
        translator = MachineTranslator()

        for lang in sorted(filenames.keys()):

            output = translator.translate(lang, content)
            with open(filenames[lang], "w") as file_out:

                file_out.write(output)

                print(f"Translated {lang}")

    print('\nSaved all translations\n')
