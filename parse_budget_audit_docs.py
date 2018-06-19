#!/usr/bin/env python

from lxml import html
import requests


import pdb


url = "http://www.detroitmi.gov/How-Do-I/View-City-of-Detroit-Reports/Budget-Audit-and-other-Financial-Reports"

page = requests.get(url)
tree = html.fromstring(page.content)
# reports = tree.xpath('//div[@class="dnntitle"]/text()')
reports = tree.xpath('//div[@class="dnntitle"]')

rep = reports[0]

dir(rep)

pdb.set_trace()

elts = rep.xpath('//li')
elt = elts[0]