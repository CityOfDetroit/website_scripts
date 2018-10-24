#!/usr/bin/env python

import csv
from lxml import html
import json
import requests
import sys


def parse_link(link):

    path = link.get('href')
    title = link.get('title')

    return path, title

def get_child_items(elt, tag):

    if elt.tag == tag:
        return [elt]

    items = []
    children = elt.getchildren()
    for child in children:

        tmp = get_child_items(child, tag=tag)
        if tmp is not None and len(tmp):
            items.extend(tmp)

    return items


class ReportInfo():

    def __init__(self, section, title, href):

        self.section = section
        self.report_title = title

        self.href = "https://www.detroitmi.gov" + href

    def get_data(self):

    	return [ self.section, self.report_title, self.href ]


if __name__ == '__main__':

    url = "http://archive.detroitmi.gov/How-Do-I/View-City-of-Detroit-Reports/Budget-Audit-and-other-Financial-Reports"

    content = {
        "base_path": "/sites/detroitmi.localhost/files/migrated_docs/financial-reports/",
        "reports": {}
    }

    page = requests.get(url)
    tree = html.fromstring(page.content)
    reports = tree.xpath('//div[@class="dnntitle"]')
    report_data = []

    for report in reports:

        subtitle = report.xpath('span')[0].text
        contents = report.xpath('following-sibling::div[@class="contentmain1"]')
        for div in contents:

            uls = get_child_items(elt=div, tag='ul')
            if uls is None or len(uls) == 0:

                links = get_child_items(elt=div, tag='a')
                if links is not None and len(links):
                    path, title = parse_link(link=links[0])

                    report_data.append(ReportInfo(section=subtitle, title=title, href=path))

            else:

                list_items = uls[0].xpath('li')
                for li in list_items:

                    path, title = parse_link(link=li.xpath('a')[0])

                    report_data.append(ReportInfo(section=subtitle, title=title, href=path))

    field_names = [ 'Section', 'Report Title', 'URL' ]

    writer = csv.DictWriter(sys.stdout, fieldnames=field_names, quoting=csv.QUOTE_ALL)
    writer.writeheader()

    for report in report_data:

        row_data = { item[0] : item[1] for item  in zip(field_names, report.get_data()) }
        writer.writerow(row_data)
