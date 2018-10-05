#!/usr/bin/env python

import csv
from lxml import html
import json
import requests
from selenium import webdriver


import pdb


def parse_path(path):

    path = path.replace('http://www.detroitmi.gov/Portals/0/docs/Fiscal%20Analysis/', '')

    pos = path.find('?')
    if pos > 0:
        path = path[ : pos]

    return path


def ignore_link(path):

    return ".pdf" not in path.lower()


if __name__ == '__main__':

    url = "http://www.detroitmi.gov/How-Do-I/View-City-of-Detroit-Reports/Fiscal-Analysis-Report"

    content = {
        "base_path": "/sites/detroitmi.localhost/files/migrated_docs/fiscal-analysis-reports/",
        "reports": {}
    }

    driver = webdriver.Firefox()
    driver.get(url)

    elts = driver.find_elements_by_xpath('//div[@class="dt-faq-item"]')
    for elt in elts:

        elt.click()

    elts = driver.find_elements_by_xpath('//div[@class="dt-faq-item"] | //a')
    for elt in elts:

        if elt.tag_name == 'div' and elt.text:

            section = elt.text.strip()
            content["reports"][section] = []

        else:

            path = elt.get_attribute('href')
            if path and not ignore_link(path):

                title = (elt.text or elt.get_attribute('title')).strip()
                path = parse_path(path)

                if title and path:
                    content["reports"][section].append({ title : path })

    # print(json.dumps(content))


    pdb.set_trace()

