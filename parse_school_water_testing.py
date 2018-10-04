#!/usr/bin/env python

import csv
import json
import requests

from bs4 import BeautifulSoup


class WaterTestSet():
    """
    Contains set of water test results (e.g., all dps schools' water tests) to csv.
    """

    field_names = [ 'school_name', 'status', 'url', 'fix_plan_status', 'fix_plan_url' ]

    def __init__(self):

        self.tests = []

    def add(self, test_info):

        self.tests.append(test_info)

    def write(self, filename):

        with open(filename, 'w', newline='') as csvfile:

            # writer = csv.writer(filename, delimiter=',', quotechar='"')
            writer = csv.DictWriter(csvfile, fieldnames = self.field_names)

            for test in self.tests:

                row_data = { item[0] : item[1] for item  in zip(self.field_names, test.get_data()) }
                writer.writerow(row_data)


def clean_val(val):

    return val.strip()


def clean_href(href):

    path = href.replace('/Portals/0/docs/Schools/School Water Testing/', '')
    return 'http://detroitmi.theneighborhoods.org/sites/detroitmi.localhost/files/migrated_docs/school-water-testing/' + path


class WaterTestInfo():
    """
    An individual set of water test results for a given school.
    """

    def __init__(self, row):

        cols = row.find_all('td')

        name_col = cols[0]
        href_col = cols[1]
        status_col = cols[2]
        if len(cols) < 4:
            mitigation_plan_col = None
        else:
            mitigation_plan_col = cols[3]

        self.name = clean_val(name_col.text)

        if href_col.find('a'):
            href = href_col.find('a').get('href')
            self.path = clean_href(href)
        else:
            self.path = ''

        self.status = clean_val(status_col.find('strong').text)

        self.fix_plan_path = ''
        self.fix_plan_status = ''

        if self.status == 'Elevated' and mitigation_plan_col:

            child = mitigation_plan_col.findChild()
            if child:

                href = child.get('href')
                if href:
                    self.fix_plan_path = clean_href(href)

                self.fix_plan_status = clean_val(child.text)

            else:

                self.fix_plan_status = clean_val(mitigation_plan_col.text)

    def get_data(self):

        return [ self.name, self.status, self.path, self.fix_plan_path, self.fix_plan_status ]

    def is_complete(self):

        # name and status always required
        if not self.name and self.status:
            return False

        # sometimes the report is not available if the location is 'Pending'
        if not self.path:
            return self.status == 'Pending'

        return True

    def __str__(self):

        return self.name


def get_pages():

    urls = {
        "dps": "http://www.detroitmi.gov/Government/Departments-and-Agencies/Detroit-Health-Department/School-Water-Testing/DPS-Water-Testing",
        "day_care": "http://www.detroitmi.gov/Government/Departments-and-Agencies/Detroit-Health-Department/School-Water-Testing/Day-Care-Water-Testing",
        "charter": "http://www.detroitmi.gov/Government/Departments-and-Agencies/Detroit-Health-Department/School-Water-Testing/Charter-and-EAA-Water-Testing",
    }

    pages = {}
    for key, url in urls.items():

        response = requests.get(url)

        pages[key] = response.text

    return pages

def parse_pages(pages):

    test_sets = {}

    for key, page in pages.items():

        test_set = WaterTestSet()

        soup = BeautifulSoup(page, 'html.parser')
        divs = soup.find_all('div', 'det-school-water')
        for div in divs:

            rows = div.find_all('tr')
            header_parsed = False

            for row in rows:

                if header_parsed:
                    test_info = WaterTestInfo(row)
                    test_set.add(test_info)
                else:
                    header_parsed = True

        test_sets[key] = test_set

    return test_sets
        

if __name__ == "__main__":

    pages = get_pages()
    test_sets = parse_pages(pages)
    for key, test_set in test_sets.items():
        filename = key + '.csv'
        test_set.write(filename=filename)
