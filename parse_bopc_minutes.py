#!/usr/bin/env python

import csv
import re
import requests
import sys

from bs4 import BeautifulSoup


import pdb


def clean_href(href):

    if 'LinkClick.aspx' in href:
        return 'http://archive.detroitmi.gov' + href

    pos = href.find('?')
    if pos > 0:
        href = href[ : pos]

    return 'https://detroitmi.gov' + href


class ReportInfo():

    def __init__(self, year, row):

        self.year = year
        self.title = row
        self.href = None

        link = row.find_parent('a')
        if link:

            self.href = clean_href(link.get('href'))

        elif 'No Meeting Held' in row:

            pass 

        else:

            pdb.set_trace()


    def get_data(self):

        return [ self.year, self.title, self.href ]


if __name__ == '__main__':

    url = "https://detroitmi.gov/government/boards/board-police-commissioners/board-police-commissioners-meeting-minutes"

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    report_data = []

    for year in reversed(range(2011, 2019)):

        pattern = re.compile(r' ' + str(year))
        rows = soup.find_all(text=pattern)

        for row in rows:

            report_data.append(ReportInfo(year, row))

    field_names = [ 'Year', 'Title', 'URL' ]

    writer = csv.DictWriter(sys.stdout, fieldnames=field_names, quoting=csv.QUOTE_ALL, dialect=csv.unix_dialect)
    writer.writeheader()

    for report in report_data:

        row_data = { item[0] : item[1] for item  in zip(field_names, report.get_data()) }
        writer.writerow(row_data)

