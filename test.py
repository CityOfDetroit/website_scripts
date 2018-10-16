#!/usr/bin/env python

import csv
import json
import requests
import sys


import pdb


class ReportInfo():

    def __init__(self, section, sub_section, title, href):

        self.section = section
        self.sub_section = sub_section
        self.title = title
        self.href = href

    def get_data(self):

        href = "http://detroitmi.theneighborhoods.org/sites/detroitmi.localhost/files/migrated_docs/emergency-manager-reports/" + self.href
        return [ self.section, self.sub_section, self.title, href ]


if __name__ == '__main__':

    url = "https://apis.detroitmi.gov/data_cache/emergency_manager_docs/?format=json"
    response = requests.get(url)

    data = response.json()
    reports = []

    data = data['data']['reports']
    for section in data.keys():

        section_data = data[section]
        if type(section_data) is dict:

            for sub_section in section_data.keys():

                for report in data[section][sub_section]:

                    report_data = tuple(report.popitem())
                    reports.append(ReportInfo(section=section, sub_section=sub_section, title=report_data[0], href=report_data[1]))

        else:

            for report in section_data:

                report_data = tuple(report.popitem())
                reports.append(ReportInfo(section=section, sub_section='', title=report_data[0], href=report_data[1]))

    field_names = [ 'Section', 'Sub Section', 'Report Title', 'URL' ]

    writer = csv.DictWriter(sys.stdout, fieldnames=field_names, quoting=csv.QUOTE_ALL)
    writer.writeheader()

    for report in reports:

        row_data = { item[0] : item[1] for item  in zip(field_names, report.get_data()) }
        writer.writerow(row_data)
