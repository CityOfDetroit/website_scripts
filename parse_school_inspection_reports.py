#!/usr/bin/env python

import csv
import json
import requests
import sys

from bs4 import BeautifulSoup


url = "http://archive.detroitmi.gov/How-Do-I/Find/School-Inspection-Reports"

def get_text(obj):

    tmp = obj.text.strip()
    return tmp if tmp else None

def get_link(obj):

    link = obj.findChild('a')
    if link:
        return link.get('href')

    return None


if __name__ == '__main__':

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    report_data = []

    field_names = [ 
        'Certificate of Compliance', 'School Name', 'School Type',
        'Safety Inspection Date', 'Safety Inspection Report',
        'Safety Re-Inspection Date', 'Safety Re-Inspection Report',
        'Health Inspection Date', 'Health Inspection Report',
        'Health Re-Inspection Date', 'Health Re-Inspection Report',
    ]

    writer = csv.DictWriter(sys.stdout, fieldnames=field_names, quoting=csv.QUOTE_ALL, dialect=csv.unix_dialect)
    writer.writeheader()

    div = soup.find("div", {"class": "contentmain1"})
    table = div.find("table")

    first_row = True

    rows = table.find_all('tr')
    for row in rows:

        if first_row:

            first_row = False
            continue

        cols = row.find_all('td')

        # Parse cert of compliance
        coc = cols[0]
        coc_link = get_link(coc)

        # Parse school name
        school_name = get_text(obj=cols[1])

        # Parse school type
        school_type = get_text(obj=cols[2])

        # Parse safety inspection date
        insp_date = cols[3]
        insp_link = get_link(insp_date)
        insp_date = get_text(obj=insp_date)

        # Parse safety re-inspection date
        re_insp_date = cols[4]
        re_insp_link = get_link(re_insp_date)
        re_insp_date = get_text(obj=re_insp_date)

        # Health inspection date
        health_date = cols[5]
        health_link = get_link(health_date)
        health_date = get_text(obj=health_date)

        # Health re-inspection date
        re_health_date = cols[6]
        re_health_link = get_link(re_health_date)
        re_health_date = get_text(obj=re_health_date)

        data = [ coc_link, school_name, school_type, insp_date, insp_link, re_insp_date, re_insp_link, health_date, health_link, re_health_date, re_health_link ]

        row_data = { item[0] : item[1] for item in zip(field_names, data) }

        writer.writerow(row_data)
