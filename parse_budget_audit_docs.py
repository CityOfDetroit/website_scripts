#!/usr/bin/env python

import csv
import json
import requests
import sys

from bs4 import BeautifulSoup


class ReportInfo():

    def __init__(self, section, title, href):

        self.section = section
        self.report_title = title

        href = href.replace(' ', '%20')
        pos = href.rfind('/')
        href = href[ pos + 1: ]
        pos = href.find('?')
        if pos > 0:
            href = href[ : pos ]

        self.href = "https://detroitmi.gov/sites/detroitmi.localhost/files/migrated_docs/financial-reports/" + href

    def get_data(self):

    	return [ self.section, self.report_title, self.href ]

url = "http://archive.detroitmi.gov/How-Do-I/View-City-of-Detroit-Reports/Budget-Audit-and-other-Financial-Reports"
dirs = [ "/portals/0/docs/budgetdept/", "/portals/0/docs/finance/" ]

def do_get_report(href):

    for tmp in dirs:

        if tmp in href.lower():
            return True

    return False


if __name__ == '__main__':

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    report_data = []

    list_items = soup.find_all('li')
    for list_item in list_items:

        link = list_item.findChild('a')
        if link:

            href = link.get('href')
            if do_get_report(href):

                span = link.find_previous('div', 'dnntitle')
                section = span.text.strip()

                report_data.append(ReportInfo(section=section, title=link.text.strip(), href=href))

    field_names = [ 'Section', 'Report Title', 'URL' ]

    writer = csv.DictWriter(sys.stdout, fieldnames=field_names, quoting=csv.QUOTE_ALL, dialect=csv.unix_dialect)
    writer.writeheader()

    for report in report_data:

        row_data = { item[0] : item[1] for item  in zip(field_names, report.get_data()) }
        writer.writerow(row_data)
