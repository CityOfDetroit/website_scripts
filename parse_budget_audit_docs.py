#!/usr/bin/env python

from lxml import html
import requests


import pdb


def parse_list_item(li):


	pdb.set_trace()

	link = li.xpath('a')



def get_item(elt, tag):

	if elt.tag == tag:
		return elt

	children = elt.getchildren()
	for child in children:

		item = get_item(child, tag=tag)
		if item is not None:
			return item


if __name__ == '__main__':

	url = "http://www.detroitmi.gov/How-Do-I/View-City-of-Detroit-Reports/Budget-Audit-and-other-Financial-Reports"

	page = requests.get(url)
	tree = html.fromstring(page.content)
	reports = tree.xpath('//div[@class="dnntitle"]')

	for report in reports:

		subtitle = report.xpath('span')[0].text
		print(subtitle)

		contents = report.xpath('following-sibling::div[@class="contentmain1"]')
		for div in contents:

			ul = get_item(div, tag='ul')

			if ul is not None:

				list_items = ul.xpath('li')
				for li in list_items:

					parse_list_item(li)

					print(list_item.text)