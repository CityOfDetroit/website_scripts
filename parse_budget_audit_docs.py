#!/usr/bin/env python

from lxml import html
import json
import requests


def parse_link(link):

	path = link.get('href')
	title = link.get('title')

	pos = path.rfind('/')
	if pos >= 0:
		path = path[pos + 1 : ]

	pos = path.find('?')
	if pos > 0:
		path = path[ : pos]

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


if __name__ == '__main__':

	url = "http://www.detroitmi.gov/How-Do-I/View-City-of-Detroit-Reports/Budget-Audit-and-other-Financial-Reports"

	content = {
		"base_path": "/sites/detroitmi.localhost/files/migrated_docs/financial-reports/",
		"reports": {}
	}

	page = requests.get(url)
	tree = html.fromstring(page.content)
	reports = tree.xpath('//div[@class="dnntitle"]')

	for report in reports:

		reports = []
		contents = report.xpath('following-sibling::div[@class="contentmain1"]')
		for div in contents:

			uls = get_child_items(elt=div, tag='ul')
			if uls is None or len(uls) == 0:

				links = get_child_items(elt=div, tag='a')
				if links is not None and len(links):
					path, title = parse_link(link=links[0])
					reports.append({ title : path })

			else:

				list_items = uls[0].xpath('li')
				for li in list_items:

					path, title = parse_link(link=li.xpath('a')[0])
					reports.append({ title : path })

		if reports:
			subtitle = report.xpath('span')[0].text
			content["reports"][subtitle] = reports

	print(json.dumps(content))
