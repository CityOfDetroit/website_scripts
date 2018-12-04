#!/usr/bin/env python

import os
import sys
import json
from datetime import date
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth

from util import get_secrets

import all_site_urls
import translated_urls


import pdb


# REVIEW:  remove all medical marijuana links?


server = "http://detroitmi.theneighborhoods.org"

# urls = []

# urls = translated_urls.all_urls
urls = all_site_urls.all_site_urls

# urls = translated_urls.city_council_urls
# urls = translated_urls.ddot_urls
# urls = translated_urls.dfd_urls
# urls = translated_urls.dpd_urls
# urls = translated_urls.bseed_urls
# urls = translated_urls.pdd_urls
# urls = translated_urls.dah_urls
# urls = translated_urls.city_clerk_urls
# urls = translated_urls.mayors_office_urls
# urls = translated_urls.dwsd_urls
# urls = translated_urls.media_services_urls
# urls = translated_urls.ocfo_urls
# urls = translated_urls.don_urls
# urls = translated_urls.dpw_urls
# urls = translated_urls.health_urls
# urls = translated_urls.hrd_urls
# urls = translated_urls.board_urls
# urls = translated_urls.faq_urls


class ContentExporter():

    output_errs = False
    error_cnt = {}
    urls_exported = {}

    auth_values = tuple(get_secrets()['CREDENTIALS']['DETROITMI'].values())

    # max_date_changed = date(year=2018, month=9, day=1)

    @staticmethod
    def report_err(msg, desc):
        if ContentExporter.output_errs:
            print("ERROR:  " + msg)
        cnt = ContentExporter.error_cnt.get(desc, 1)
        ContentExporter.error_cnt[desc] = cnt + 1

    @staticmethod
    def report_err_cnt():
        if ContentExporter.output_errs:
            print('\n**************************************************************************************\n')
            print('errors:  ' + str(ContentExporter.error_cnt))
            print('num successful exports: ' + str(len(ContentExporter.urls_exported)))

    @staticmethod
    def in_review(content):

        for key in [ 'field_need_review', 'field_need_reviewed' ]:
            if content.get(key) and content[key][0]['value']:
                # pdb.set_trace()
                return True

        tmp_content = str(content)
        for word in [ 'TODO', 'REVIEW' ]:
            if word in tmp_content:
                # pdb.set_trace()
                return True

        return False

    @staticmethod
    def needs_translation(content):

        if not content:
            pdb.set_trace()
            return True

        changed = content.get('changed')
        if not changed:
            pdb.set_trace()
            return True

        tmp = changed[0]['value']
        date_changed = datetime.strptime(tmp[0 : 10], '%Y-%m-%d').date()
        # if ContentExporter.max_date_changed and date_changed >= ContentExporter.max_date_changed:
        #     return True

        for key in [ "field_dept_translation_date", "field_gov_translation_date" ]:

            if content.get(key):

                tmp = content[key][0]['value']
                translation_date = datetime.strptime(tmp[:10], '%Y-%m-%d').date()
                if translation_date < date_changed:
                    return True
                else:

                    return False

        return False

    @staticmethod
    def get_div(content, content_id, start=0):

        # Try to find the identifier
        id_pos = content.find(content_id, start)
        if id_pos == -1:
            return [None, None]

        # Now try to find the beginning of the div containing it
        begin = content.rfind("<div", 0, id_pos)
        if begin == -1:
            pdb.set_trace()
            return [None, None]

        # Find end of <div tag
        content_begin = content.find(">", begin + 4)
        if content_begin == -1:
            pdb.set_trace()
            return [None, None]

        # Finally, try to find closing </div>
        end = content.find("</div>", content_begin + 1)
        if end == -1:
            pdb.set_trace()
            return [None, None]

        sub_string = content[content_begin + 1 : end]
        return [ sub_string, end ]

    @staticmethod
    def export_faq_pair(faq_pair):

        target_id = faq_pair['target_id']

        url = "{}/rest/translation/paragraph/{}".format(server, target_id)

        response = requests.get(url + "?_format=json")
        if response.status_code != 200:
            ContentExporter.report_err("url {} got status code {}".format(url, response.status_code), response.status_code)
            return;

        json = response.json()
        content = json[0]['bp_accordion_section']

        faq_pairs = []
        start = 0

        while True:

            question, start = ContentExporter.get_div(content=content, content_id="field--name-bp-accordion-section-title", start=start)
            answer, start = ContentExporter.get_div(content=content, content_id="field--name-bp-text", start=start)

            if not question or not answer:
                return faq_pairs

            faq_pairs.append( { "question": question, "answer": answer } )

    @staticmethod
    def handle_howdoi(url, data):

        if "how-do-i" not in url.lower():
            return None

        for key in ['field_department']:

            related = data.get(key)
            if related:
                tmp_url = related[0].get('url', '')
                if tmp_url:
                    return tmp_url

        # we did not find good related content, so don't try to retrieve any
        return None

    @staticmethod
    def handle_faq(data):

        field_faq_refer = data.get('field_faq_refer')
        if field_faq_refer:
            url = field_faq_refer[0].get('url')
            if url:
                urls.append(url)

    @staticmethod
    def cleanup_url(url):

        pos = url.find('?')
        if pos > 0:
            url = url[0 : pos]
        return url

    @staticmethod
    def get_response_url(url, response):

        tmp = response.url
        if "/node/" not in tmp:
            url = tmp
        return url

    @staticmethod
    def get_data(url):

        url = "{}{}".format(server, url)

        response = requests.get(url + "?_format=json", auth=HTTPBasicAuth(*ContentExporter.auth_values))
        if response.status_code != 200:
            ContentExporter.report_err("url {} got status code {}".format(url, response.status_code), response.status_code)
            return [None, None];

        url = response.url

        # Have we already exported this content?
        tmp_url = ContentExporter.cleanup_url(response.url)
        if ContentExporter.urls_exported.get(tmp_url):
            ContentExporter.report_err("url {} has already been exported".format(tmp_url), "Duplicate URL")
            return [None, None];

        data = response.json()
        tmp_url = ContentExporter.handle_howdoi(url, data)
        ContentExporter.handle_faq(data)
        if tmp_url:
            return ContentExporter.get_data(url=tmp_url)
        else:
            return url, data

    @staticmethod
    def do_export(url, options={}):

        url, data = ContentExporter.get_data(url=url)
        if not url:
            return

        if not ContentExporter.needs_translation(data):
            ContentExporter.report_err("url {} does not need translation".format(url), "No translation needed")
            return

        if options.get('skip_review_pages', True) and ContentExporter.in_review(data):
            ContentExporter.report_err("url {} is still in REVIEW".format(url), "REVIEW status")
            return

        # Handle any faq pairs
        for idx, faq_pair in enumerate(data.get('field_faq_pair', [])):

            if faq_pair['target_type'] == 'paragraph':

                parsed_faq_pairs = ContentExporter.export_faq_pair(faq_pair=faq_pair)
                data['field_faq_pair'][idx]['content'] = parsed_faq_pairs

            else:
                pdb.set_trace()

        url = ContentExporter.cleanup_url(url)
        print("url: " + url)

        has_some_required = False
        required_keys = set(data.keys()).intersection(["description", "summary", "field_faq_pair"])
        for key in required_keys:

            if data.get(key):
                has_some_required = True

        if not has_some_required:
            ContentExporter.report_err("url {} was missing required data".format(url), "Missing required data")
            return 

        # print(json.dumps(data))
        ContentExporter.urls_exported[url] = True
        # print("")

        if ContentExporter.output_errs:
            return

        # also print the json to an individual file for each url
        url_encoded = url[37 : ].replace("/", "%2F")
        url_encoded = ContentExporter.cleanup_url(url_encoded)

        if options.get('write_to_file', True):
            with open(url_encoded + ".txt", 'w') as output:

                output.write(ContentExporter.cleanup_url(url) + "\n\n")
                output.write(json.dumps(data))

        return url, data


if __name__ == '__main__':

    if len(sys.argv) == 2:
        ContentExporter.output_errs = sys.argv[1] == '--debug=true'

    for url in urls:

        ContentExporter.do_export(url=url)

    ContentExporter.report_err_cnt()
