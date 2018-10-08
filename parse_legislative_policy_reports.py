#!/usr/bin/env python

import csv
from lxml import html
import json
import requests
import sys
from selenium import webdriver


def parse_path(path):

    path = path.replace('http://www.detroitmi.gov/Portals/0/docs/Legislative%20Policy%20Reports/', '')

    pos = path.find('?')
    if pos > 0:
        path = path[ : pos]

    return path


def ignore_link(path):

    return ".pdf" not in path.lower()


class ReportInfo():

    def __init__(self, section, sub_section, report_title, href):

        self.section = section
        self.sub_section = sub_section
        self.report_title = report_title
        self.href = href

    def get_data(self):

        return [ self.section, self.sub_section, self.report_title, self.href ]

if __name__ == '__main__':

    url = "http://www.detroitmi.gov/How-Do-I/View-City-of-Detroit-Reports/Legislative-Policy-Division-Reports"

    reports = []
    section = ''
    sub_section = ''
    report_title = ''
    href = ''

    driver = webdriver.Firefox()
    driver.get(url)

    elts = driver.find_elements_by_xpath('//div[@class="dt-faq-item"]')
    for elt in elts:

        elt.click()

    elts = driver.find_elements_by_xpath('//div[@class="dnntitle"] | //div[@class="dt-faq-item"] | //a')
    for elt in elts:

        if elt.tag_name == 'div' and elt.text:

            if elt.get_attribute('class') == 'dnntitle':

                tmp = elt.find_element_by_tag_name('span')
                if tmp:
                    section = tmp.text.strip()

            else:

                sub_section = elt.text.strip()

        else:

            href = elt.get_attribute('href')
            if href and not ignore_link(href):

                title = (elt.get_attribute('title') or elt.text).strip()
                href = parse_path(href)

                if title and href:

                    href = "http://detroitmi.theneighborhoods.org/sites/detroitmi.localhost/files/migrated_docs/legislative-policy-reports/" + href

                    report_info = ReportInfo(section, sub_section, title, href)
                    reports.append(report_info)

    field_names = [ 'Section', 'Sub Section', 'Report Title', 'URL' ]

    # writer = csv.writer(filename, delimiter=',', quotechar='"')
    writer = csv.DictWriter(sys.stdout, fieldnames=field_names, quoting=csv.QUOTE_ALL)
    writer.writeheader()

    for report in reports:

        row_data = { item[0] : item[1] for item  in zip(field_names, report.get_data()) }
        writer.writerow(row_data)
