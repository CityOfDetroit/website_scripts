#!/usr/bin/env python
import os
import sys
import json
from datetime import date
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth

import crawler
import translated_urls


translated_urls = translated_urls.city_council_urls + translated_urls.ddot_urls + translated_urls.dfd_urls \
 + translated_urls.dpd_urls + translated_urls.bseed_urls + translated_urls.pdd_urls + translated_urls.dah_urls \
 + translated_urls.city_clerk_urls + translated_urls.mayors_office_urls + translated_urls.dwsd_urls \
 + translated_urls.media_services_urls + translated_urls.ocfo_urls + translated_urls.don_urls \
 + translated_urls.dpw_urls + translated_urls.health_urls + translated_urls.hrd_urls \
 + translated_urls.board_urls + translated_urls.faq_urls


def print_msg(msg):
    print(msg)
    sys.stdout.flush()


class MachineURLFinder():

    domain = "detroitmi.gov"
    site = "https://" + domain

    num_urls_processed = 0

    def print_progress(self, urls):

        curr_num_urls = len(urls)
        if curr_num_urls - self.num_urls_processed == 10 or curr_num_urls < self.num_urls_processed:
            print_msg("progress:  {} urls processed".format(curr_num_urls))
            self.num_urls_processed = curr_num_urls

    def set_translated_urls(self, urls):

        tmp_urls = []

        for url in translated_urls:

            response = requests.get(self.site + url)
            if response.ok:

                tmp_urls.append(response.url.strip().lower())
                self.print_progress(tmp_urls)

        self.translated_urls = tmp_urls

    def set_all_urls(self):

        admin = crawler.PageCrawlerAdmin()

        # Start crawling the site.
        admin.crawl_page(domain=self.domain, url=self.site)
        self.all_urls = admin.get_urls_crawled()

    def get_machine_translated_urls(self):

        urls = [ url for url in self.all_urls if url not in self.translated_urls ]
        return sorted(urls)


if __name__ == '__main__':

    finder = MachineURLFinder()

    print_msg("Get our translated urls")

    finder.set_translated_urls(translated_urls)

    print_msg("Now get our full list of urls")

    finder.set_all_urls()

    print_msg("Finally, just print each url that is machine translated")

    for url in finder.get_machine_translated_urls():
        print(url)
