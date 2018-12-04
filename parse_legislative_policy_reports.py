#!/usr/bin/env python

import csv
import re
import requests
import sys
from selenium import webdriver
from bs4 import BeautifulSoup


def find_elts(tag):

    if tag.name == 'a':

        return True

    if tag.name == 'div':

        klass = tag.get('class', '')
        return klass and set(klass) & set(["dnntitle", "dt-faq-item"])

    return False

def parse_path(path):

    tmp_path = path.lower()

    for folder in ['/legislative%20policy%20reports/', '/legislative policy reports/']:
        if folder in tmp_path:

            pos = tmp_path.find(folder)
            path = path[pos + len(folder) : ]
            break

    pos = path.find('?')
    if pos > 0:
        path = path[ : pos]

    return path

def ignore_link(path):

    return ".pdf" not in path.lower()


def clean_title(title):

    replacements = [
        ("\xa0", ' ')
    ]

    for replacement in replacements:
        title = title.replace(replacement[0], replacement[1])

    return title


class ReportInfo():

    def __init__(self, section, sub_section, report_title, href, display_order):

        self.section = section
        self.sub_section = sub_section
        self.report_title = report_title
        self.href = href
        self.display_order = display_order

    def get_data(self):

        return [ self.section, self.sub_section, self.report_title, self.href, self.display_order ]

if __name__ == '__main__':

    url = "http://archive.detroitmi.gov/How-Do-I/View-City-of-Detroit-Reports/Legislative-Policy-Division-Reports"

    reports = []
    section = ''
    sub_section = ''
    report_title = ''
    href = ''
    report_dates = []
    report_dates_set = False

    driver = webdriver.Firefox()
    driver.get(url)

    elts = driver.find_elements_by_xpath('//div[@class="dt-faq-item"]')
    for elt in elts:

        elt.click()

    soup = BeautifulSoup(driver.page_source, 'html.parser')


    # REVIEW:  Not sure why this doesn't work
    # elts = soup.find_all(lambda tag: tag.name == 'a' or (tag.name == 'div' and set(tag.get('class', '')) & set(["dnntitle", "dt-faq-item"])))


    elts = soup.find_all(find_elts)
    for elt in elts:

        if elt.name == 'div' and elt.text:

            if 'dnntitle' in elt.get('class', []):

                tmp = elt.find('span')
                if tmp:
                    section = tmp.text.strip()

            else:

                sub_section = elt.text.strip()

        else:

            href = elt.get('href')
            if href and not ignore_link(href):


                if sub_section == '2018 Reports to Council':

                    if not report_dates_set:

                        report_dates = re.findall(r'2018-[0-9]{2}-[0-9]{2}', elt.parent.text)
                        report_dates.reverse()
                        report_dates_set = True

                else:

                    report_dates = []

                title = (elt.text or elt.name).strip()
                title = clean_title(title)

                if report_dates:

                    title = report_dates.pop() + ': ' + title

                href = parse_path(href)

                if title and href:

                    href = "https://detroitmi.gov/sites/detroitmi.localhost/files/migrated_docs/legislative-policy-reports/" + href

                    report_info = ReportInfo(section, sub_section, title, href, len(reports) + 1)
                    reports.append(report_info)

    field_names = [ 'Section', 'Sub Section', 'Report Title', 'URL', 'Display Order' ]

    writer = csv.DictWriter(sys.stdout, fieldnames=field_names, quoting=csv.QUOTE_ALL, dialect=csv.unix_dialect)
    writer.writeheader()

    for report in reports:

        row_data = { item[0] : item[1] for item  in zip(field_names, report.get_data()) }
        writer.writerow(row_data)
