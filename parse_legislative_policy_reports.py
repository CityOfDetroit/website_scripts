#!/usr/bin/env python

from lxml import html
import json
import requests
from selenium import webdriver


def parse_path(path):

    path = path.replace('http://www.detroitmi.gov/Portals/0/docs/Legislative%20Policy%20Reports/', '')

    pos = path.find('?')
    if pos > 0:
        path = path[ : pos]

    return path


def ignore_link(path):

    return ".pdf" not in path.lower()


if __name__ == '__main__':

    url = "http://www.detroitmi.gov/How-Do-I/View-City-of-Detroit-Reports/Legislative-Policy-Division-Reports"

    content = {
        "base_path": "/sites/detroitmi.localhost/files/migrated_docs/legislative-policy-reports/",
        "reports": {}
    }

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
                    content["reports"][section] = {}

            else:

                subtitle = elt.text.strip()
                content["reports"][section][subtitle] = []

        else:

            path = elt.get_attribute('href')
            if path and not ignore_link(path):

                title = (elt.get_attribute('title') or elt.text).strip()
                path = parse_path(path)

                if title and path:
                    content["reports"][section][subtitle].append({ title : path })

    print(json.dumps(content))
