#!/usr/bin/env python

from datetime import datetime
import re
import requests
import sys


class Urls():

    def __init__(self, domain, content):
        self.domain = domain
        self.content = content

    def build_url(self, url):
        """
        Clean up url:
        - make url all-lowercase
        - make sure protocol is http, not https (again, to avoid dupes)
        - make sure domain is present
        - 'normalize' the domain (remove 'www') to avoid dupes
        - attempt to remove multiple repeated ';amp' values.
        """

        url = url.lower()

        if url.startswith('https://'):
            url = url.replace('https://', 'http://')

        if url.startswith('/'):
            url = 'http://' + self.domain + url

        if url.startswith('http://www.'):
            url = url.replace('http://www.', 'http://')

        # find 'end' of url
        url_endings = ['#', '?']
        for url_ending in url_endings:
            pos = url.find(url_ending)
            if pos > 0:
                url = url[ : pos]

        remove_strings = [
            "amp;",
        ]

        for remove_string in remove_strings:
            url = re.sub(remove_string, '', url)

        if url.endswith('/'):
            url = url[ : -1]

        return url

    def ignore_url(self, url):
        """
        Returns True if we should ignore the url.
        """

        url = url.lower()

        # Verify valid protocol (e.g., avoid "tel:", "mailto:")
        valid_protocols = [
            "http:",
            "https:",
        ]

        protocol_ok = False
        for protocol in valid_protocols:

            if url.startswith(protocol):
                protocol_ok = True

        if not protocol_ok:
            return True

        # Make sure file type (if any) is one we are interested in
        ignored_endings = [
            ".css",
            "/css",
            ".ico",
            ".png",
            ".jpg",
            ".pdf",
            ".axd",
        ]

        for ignore in ignored_endings:

            if url.endswith(ignore):
                return True

        # For now, ignore url unless it has our domain
        if self.domain not in url:
            return True

        # Make sure path is one we are interested in
        ignored_paths = [
            "/search-results",
            "/calendar-and-events/",
            "/calendar-events/",
            "/cablecastpublicsite/",
            "/dnngo_xblog/",
            "/portals/0/docs/",
            "/bundles/styles/",
            "codstaging.detroitmi.gov",
            "data.detroitmi.gov",
            "dev.socrata.com",
            "detroit-archives",
            "articleid",
            "github.com",
            "how-do-i/index-a-to-z",
            "/home/ctl",
            "/homeold",
            "city-council-sessions/m",
            "goo.gl/",
            "govdelivery.com",
            "/home-old/",
            "/news/",
            "/register/mitn",
            "/login",
            "board-of-zoning-appeal-calendar",
            "health-department-news-and-alerts",
            "health-calendar",
            "ddot-news-and-alerts",
            "serve-detroit/newsandalerts",
            "linkclick.aspx",
        ]

        ignored_paths.extend(
                [
                    "/devel/",
                    "/document/",
                    "/forms/",
                    "/taxonomy/",
                    "/taxonomy_term/",
                    "/media/",
                    "/node",
                ]
            )

        # for now, avoid crawling translations so we don't "double-count" pages
        ignored_paths.extend(
                [
                    "/en/",
                    "/es/",
                    "/ar/",
                    "/bn/",
                ]
            )

        for ignore in ignored_paths:

            if ignore in url:
                return True

        return False

    def next_url(self):


        illegal = "2cfb2a637f0f49e197ef78e397e76eb9"

        if illegal in self.content:
            print("spotted illegal tag")

        begin = re.search('href=[\'\"]', self.content)
        if not begin:
            raise StopIteration

        self.content = self.content[begin.end() : ]
        end = re.search('[\'\"]', self.content)
        if not end:
            raise StopIteration

        url = self.content[ : end.start()]
        url = self.build_url(url)

        if self.ignore_url(url):
            return self.next_url()

        return url

    def __iter__(self):
        return self

    def __next__(self):
        """
        Return next url in the page, if any.
        """

        return self.next_url()


class PageCrawler():

    url_map = {}

    def __init__(self, domain, url):

        self.domain = domain
        self.url = url

    def urls(self):

        response = requests.get(self.url)
        if response.status_code != 200 or self.domain not in response.url:
            # print("url {} - {}".format(url, response.status_code))
            return []

        # Is the page in review?
        if self.in_review(content=response.text):
            print("Page {} is IN REVIEW".format(response.url))

        # Does the page have invalid urls?
        if self.has_bad_links(content=response.text):
            print("Page {} has BAD LINKS".format(response.url))

        self.url_map[self.url] = response.url
        return Urls(domain=self.domain, content=response.text)

    def map_urls(self, urls):

        urls_tmp = set()
        for url in urls:
            urls_tmp.add(self.url_map.get(url, url))

        return urls_tmp

    def in_review(self, content):

        tmp_content = str(content)
        for word in [ 'TODO', 'ToDo', 'REVIEW' ]:
            if word in tmp_content:
                return True

        return False

    def has_bad_links(self, content):

        tmp_content = str(content).lower()
        for link_val in [ 'linkclick.aspx', '/portals/' ]:

            if link_val in content:
                return True

        return False


class PageCrawlerAdmin():

    MAX_LEVELS_DEEP = 250
    ILLEGAL_DOMAIN = "detroitmi.gov"

    def __init__(self):

        self.urls_crawled = set()
        self.levels_deep = 0

    def is_domain_illegal(url):

        for begin in [ "://www.", "://" ]:

            pos = url.find(begin)
            if pos > 0:

                url = url[ pos + len(begin) : ]
                break

        return url.startswith(PageCrawlerAdmin.ILLEGAL_DOMAIN)

    def crawl_page(self, domain, url):

        if len(self.urls_crawled) > 4000:
            print("Max urls attained")
            return

        if self.levels_deep == self.MAX_LEVELS_DEEP:
            print("Too many levels deep")
            return

        self.crawler = PageCrawler(domain=domain, url=url)

        self.levels_deep = self.levels_deep + 1

        for url in self.crawler.urls():

            if url not in self.urls_crawled:

                if PageCrawlerAdmin.is_domain_illegal(url):
                    print("ILLEGAL DOMAIN: " + url)

                self.urls_crawled.add(url)

                if len(self.urls_crawled) % 100 == 0:
                    print("crawled {} urls - {}".format(len(self.urls_crawled), datetime.now()))
                    sys.stdout.flush()

                print("level: {} - url: {}".format(self.levels_deep, url), file=sys.stderr)
                sys.stderr.flush()

                # If this url is on our domain then crawl it.
                if domain in url:
                    self.crawl_page(domain=domain, url=url)

        self.levels_deep = self.levels_deep - 1

    def get_urls_crawled(self):

        self.urls_crawled = self.crawler.map_urls(self.urls_crawled)
        return self.urls_crawled


if __name__ == '__main__':

    domain = "detroitmi.gov"
    site = "https://" + domain

    admin = PageCrawlerAdmin()

    # Start crawling the site.
    try:
        admin.crawl_page(domain=domain, url=site)
    except RecursionError:
        print("Caught RecursionError")
    except:
        print("Caught Unknown Error")

    urls_crawled = admin.get_urls_crawled()

    for url in sorted(list(urls_crawled)):
        print(url)
