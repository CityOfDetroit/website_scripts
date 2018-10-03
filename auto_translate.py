#!/usr/bin/env python

import sys
import time

from google.cloud import translate

from bs4 import BeautifulSoup

from parse_translated_content import TranslatedPage
from export_translations import ContentExporter
import load_translation


class MachineTranslatorHelper():
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


class AutoTranslator():
    """
    Class for machine-translating and saving (when appropriate) content.
    """

    def __init__(self, url):
        """
        Initialize object with url to be translated.
        """

        if url.startswith('http'):
            url = url[7 : ]

            pos = url.find('/')
            url = url[pos : ]

        self.url = url
        self.translated_pages = {}
        self.translator = MachineTranslatorHelper()

    def get_source_content(self):
        """
        Extract source content to be translated.
        """

        # Extract the content to be translated
        options={'write_to_file': False, 'skip_review_pages': False}
        tmp = ContentExporter.do_export(url=self.url, options=options)
        if not tmp:

            ContentExporter.output_errs = True
            ContentExporter.do_export(url=url, options=options)
            ContentExporter.report_err_cnt()
            raise Exception('content could not be exported')

        true_url, data = tmp
        return data

    def translate_content(self, data):
        """
        Translate the content into all languages.
        """

        source_page = TranslatedPage()
        source_page.parse_json(data)

        for lang in sorted(TranslatedPage.LANG_MAP.keys()):

            # Translate the content
            translated_page = TranslatedPage()

            translated_page.vid = source_page.vid
            translated_page.nid = source_page.nid
            translated_page.tid = source_page.tid

            translated_page.content = self.translator.translate(lang=lang, text=source_page.content)
            translated_page.title = self.translator.translate(lang=lang, text=source_page.title)
            translated_page.desc = self.translator.translate(lang=lang, text=source_page.desc)
            translated_page.organization_head_information = self.translator.translate(lang=lang, text=source_page.organization_head_information)
            translated_page.summary = self.translator.translate(lang=lang, text=source_page.summary)

            # translate any faq content
            for faq_pair in source_page.faq:

                question = self.translator.translate(lang=lang, text=faq_pair['question'])
                answer = self.translator.translate(lang=lang, text=faq_pair['answer'])

                translated_page.faq.append({'question': question, 'answer': answer})

            self.translated_pages[lang] = translated_page

    def save_translations(self):
        """
        Save the translated content to database or to file, as appropriate
        (at this point we are writing data that is not in a taxonomy to a file
        so that it can be loaded manually).
        """

        # Now write the translated content
        for lang, translated_page in self.translated_pages.items():

            if translated_page.faq:

                # Output translated faq content to file
                filename = "{}_{}.txt".format(translated_page.nid, lang)
                print("Writing faq content to {}".format(filename))
                output = open(filename, mode='w')
                translated_page.output_file(output=output, url=self.url, lang=lang)

            else:

                load_translation.Loader().run_page(lang, translated_page)


if __name__ == '__main__':

    # Usage:  auto_translate.py <url>
    #  e.g.,  auto_translate.py 'http://detroitmi.theneighborhoods.org/departments/police-department'
    #  e.g.,  auto_translate.py '/departments/police-department'

    if len(sys.argv) != 2:
        raise Exception("Usage:  <url>")

    translator = AutoTranslator(url=sys.argv[1])

    # Extract content to be translated.
    data = translator.get_source_content()

    # Translate the content
    translator.translate_content(data)

    # Save translations
    translator.save_translations()
 
    print('\nLoaded all translations\n')
