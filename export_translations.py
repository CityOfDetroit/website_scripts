#!/usr/bin/env python
import os
import sys
import json
from datetime import date
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth

import django
from django.conf import settings


import pdb


# REVIEW:  remove all medical marijuana links?


server = "http://detroitmi.theneighborhoods.org"
urls = [
    "/2016-Crime-Statistics",
    "/Boards/BoardOfPoliceCommissioners",
    "/BSEED",
    "/businessincometax",
    "/Calendar-and-Events",
    "/Calendar-Events",
    "/CampauBanglatown",
    "/Correspondence",
    "/DACC",
    "/DDOT",
    "/Demolition",
    "/Detroit-Dashboard",
    "/Detroit-Demolition-Program/View-All-Demolitions",
    "/Detroit-Opportunities",
    "/Detroit-Opportunities/Find-A-Job",
    "/Detroit-Opportunities/Help-with-your-Home",
    "/Detroit-Opportunities/Programs-for-Youth",
    "/Detroit-Opportunities/Start-or-Grow-Your-Business",
    "/Detroit-Opportunities/Start-or-Grow-Your-Business/Contractor-for-Rehabbed-and-Ready-Program",
    "/doglicense",
    "/Drainage",
    "/dwsd",
    "/DWSDCustomerCare",
    "/DWSDkiosk",
    "/DWSDSkipTheLine",
    "/elections",
    "/employment",
    "/fintreasury",
    "/Government",
    "/Government/Boards",
    "/Government/Boards/Board-of-Electrical-Examiners-Forms",
    "/Government/City-Clerk",
    "/Government/City-Council",
    "/Government/City-Council/Andre-Spivey",
    "/Government/City-Council/Brenda-Jones",
    "/Government/City-Council/City-Council-Sessions",
    "/Government/City-Council/Gabe-Leland",
    "/Government/City-Council/James-Tate",
    "/Government/City-Council/Janee-L-Ayers",
    "/Government/City-Council/Mary-Sheffield",
    "/Government/City-Council/Raquel-Castaneda-Lopez",
    "/Government/City-Council/Roy-McCalister",
    "/Government/City-Council/Scott-Benson",
    "/Government/Commissions",
    "/Government/Departments",
    "/Government/Departments-and-Agencies/Detroit-Department-of-Transportation/DDOT-News-and-Alerts",
    "/Government/Departments-and-Agencies/Detroit-Health-Department/Detroit-ID",
    "/Government/Departments-and-Agencies/Detroit-Health-Department/Food-Safety",
    "/Government/Departments-and-Agencies/Detroit-Health-Department/Immunizations",
    "/Government/Departments-and-Agencies/Detroit-Health-Department/Sexually-Transmitted-Diseases",
    "/Government/Departments-and-Agencies/Law-Department",
    "/Government/Departments-and-Agencies/Office-of-the-Chief-Financial-Office/Office-of-the-Assessor",
    "/Government/Departments-and-Agencies/Planning-and-Development-Department",
    "/Government/Departments-and-Agencies/Planning-and-Development-Department/Staff-Info",
    "/Government/Departments-and-Agencies/Public-Works/Contact-us",
    "/Government/Departments-and-Agencies/Public-Works/Curbside-Bulk-Waste-Pickup",
    "/Government/Departments-and-Agencies/Public-Works/Recycle",
    "/Government/Departments-and-Agencies/Water-and-Sewerage-Department/About-DWSD",
    "/Government/Departments-and-Agencies/Water-and-Sewerage-Department/Learn-About-Your-Water-and-Sewer-Bill",
    "/Government/Detroit-Police-Commissioners-Meetings",
    "/Government/Mayors-Office",
    "/Government/Mayors-Office/Administration",
    "/health",
    "/How-Do-I",
    "/How-Do-I/Appeal",
    "/How-Do-I/Appeal/Property-Assessment-Forms",
    "/How-Do-I/Apply-for-Licenses",
    "/How-Do-I/Apply-for-Licenses/Boiler-License-Information",
    "/How-Do-I/Apply-for-Licenses/Buildings-License-Information",
    "/How-Do-I/Apply-for-Licenses/Business-License-Checklist",
    "/How-Do-I/Apply-for-Licenses/Business-License-Forms",
    "/How-Do-I/Apply-for-Permits",
    "/How-Do-I/Apply-for-Permits/Building-Inspection-Information",
    "/How-Do-I/Apply-for-Permits/Building-Permit-FAQ",
    "/How-Do-I/Apply-for-Permits/Building-Permit-Information",
    "/How-Do-I/Apply-for-Permits/Gun-Permits-Information",
    "/How-Do-I/Apply-for-Permits/Special-Events-Information",
    "/How-Do-I/Apply-for-Permits/Zoning-Map-Index",
    "/How-Do-I/Apply-for-Permits/Zoning-Permit-Forms",
    "/How-Do-I/Apply-for-Permits/Zoning-Permit-Information",
    "/How-Do-I/Construction-Division-Information",
    "/How-Do-I/Do-Business-with-the-City",
    "/How-Do-I/Do-Business-with-the-City/Building-Authority-Advertisements",
    "/How-Do-I/Do-Business-with-the-City/Open-Bids-for-the-City-of-Detroit",
    "/How-Do-I/Do-Business-with-the-City/Planning-Development-RFQs",
    "/How-Do-I/File",
    "/How-Do-I/File/Blight-Complaint",
    "/How-Do-I/File/Income-Tax-Forms",
    "/How-Do-I/File/Income-Tax-Information",
    "/How-Do-I/Find",
    "/How-Do-I/Find/Adams-Butzel-Complex",
    "/How-Do-I/Find/Birth-and-Death-Certificates",
    "/How-Do-I/Find/City-Employee-Information",
    "/How-Do-I/Find/Detroit-Animal-Care-and-Control",
    "/How-Do-I/Find/Detroit-Parks-Recreation/Hart-Plaza",
    "/How-Do-I/Find/Detroit-Parks-Recreation/Parks-Recreation-Forms",
    "/How-Do-I/Find/DPD-Jobs",
    "/How-Do-I/Find/DWSD-Alerts-and-News",
    "/How-Do-I/Find/DWSD-Associations",
    "/How-Do-I/Find/Employee-Forms",
    "/How-Do-I/Find/Hotline-Numbers",
    "/How-Do-I/Find/Medical-Marihuana-FAQs",
    "/How-Do-I/FInd/Municipal-Parking-FAQ",
    "/How-Do-I/Find/Payment-Plan",
    "/How-Do-I/Find/Police-Precincts",
    "/How-Do-I/Find/properties/Properties-FAQs",
    "/How-Do-I/Find/Recycling-Information",
    "/How-Do-I/Find/Refuse-Collection",
    "/How-Do-I/Find/Schedule-An-Appointment",
    "/How-Do-I/Find/Water-Sewer-and-Drainage-Rates-101",
    "/How-Do-I/Find-Community-Services",
    "/How-Do-I/Find-Community-Services/Arson-Awareness",
    "/How-Do-I/Find-Community-Services/Keep-the-Water-On",
    "/How-Do-I/Find-Detroit-Archives",
    "/How-Do-I/Find-Detroit-Archives/City-Clerks-Archives-and-Records-Information",
    "/How-Do-I/Find-Transportation/Buy-A-Pass",
    "/How-Do-I/Grants",
    "/How-Do-I/Index-A-to-Z/A",
    "/How-Do-I/Index-A-to-Z/P",
    "/How-Do-I/Locate-Transportation",
    "/How-Do-I/Locate-Transportation/Bus-Schedules",
    "/How-Do-I/Locate-Transportation/Bus-Schedules-Information",
    "/How-Do-I/Locate-Transportation/Metro-Lift-Requirements",
    "/How-Do-I/Locate-Transportation/Public-Notices",
    "/How-Do-I/Locate-Transportation/Transporation-Fares",
    "/How-Do-I/Medical-Marihuana-Information",
    "/How-Do-I/MobileApps",
    "/How-Do-I/Mobile-Apps/ImproveDetroit",
    "/How-Do-I/My-District",
    "/How-Do-I/Neighborhood-Police-Officer-NPO-program",
    "/How-Do-I/Neighborhood-Police-Officer-NPO-program/7TH-PRECINCT-NPO",
    "/How-Do-I/Neighborhood-Police-Officer-NPO-program/8TH-PRECINCT-NPO",
    "/How-Do-I/Neighborhood-Police-Officer-NPO-program/9TH-PRECINCT-NPO",
    "/How-Do-I/Neighborhood-Police-Officer-NPO-program/GAMING-NPO",
    "/How-Do-I/Obtain-Grant-Information/Home-Repair-Program-Information",
    "/How-Do-I/Obtain-Grant-Information/Renaissance-Zones",
    "/How-Do-I/Pay",
    "/How-Do-I/Pay/Blight-Ticket-FAQ",
    "/How-Do-I/Pay/Delinquent-Property-Tax-Information",
    "/How-Do-I/Pay/Pay-Parking-Ticket",
    "/How-Do-I/Pay/Police-Records-and-Reports-Information",
    "/How-Do-I/Pay/Property-Taxes-FAQs",
    "/How-Do-I/Pay/Property-Taxes-Information",
    "/How-Do-I/Pay/Water-Bill-Locations",
    "/How-Do-I/Property-Assessment-Documents",
    "/How-Do-I/Register",
    "/How-Do-I/Register/Register-A-Rental-Property",
    "/How-Do-I/Report",
    "/How-Do-I/Report/Abandoned-Vehicle",
    "/How-Do-I/Report/Crime",
    "/How-Do-I/Report/Dead-Animal-Removal",
    "/How-Do-I/Request-a-Service",
    "/How-Do-I/Request-a-Service/Council-Awards-and-Resolutions",
    "/How-Do-I/Request-a-Service/DPW-Container-Services",
    "/How-Do-I/Request-a-Service/Street-Maintenance",
    "/How-Do-I/Request-a-Service/Tree-Services",
    "/How-Do-I/View-City-of-Detroit-Reports",
    "/How-Do-I/View-City-of-Detroit-Reports/Legislative-Policy-Division-Reports",
    "/How-Do-I/View-Publications-and-Newsletters/Construction-Codes",
    "/How-Do-I/Volunteer/MotorCity-Makeover-Information",
    "/IncomeTax",
    "/Mayors-Help-Desk",
    "/MediaServices",
    "/MedicalMarihuana",
    "/Neighborhoods",
    "/News",
    "/parking",
    "/Police",
    "/projectcleanslate",
    "/properties",
    "/PublicWorks",
    "/Purchasing",
    "/recreation",
    "/rental",
    "/rental/property-registration",
    "/rental/Schedule-Property-Inspection",
    "/Serve-Detroit",
    "/Supplier",
    "/youthprograms",
]

output_errs = False
export_cnt = {}
error_cnt = {}


def report_err(msg, desc):
    if output_errs:
        print("ERROR:  " + msg)
    cnt = error_cnt.get(desc, 1)
    error_cnt[desc] = cnt + 1

def report_err_cnt():
    if output_errs:
        print('\n**************************************************************************************\n')
        print('errors:  ' + str(error_cnt))
        print('num successful exports: ' + str(len(export_cnt)))

def in_review(content):

    for key in [ 'field_need_review', 'field_need_reviewed' ]:
        if content.get(key) and content[key][0]['value']:
            return True

    tmp_content = str(content)
    for word in [ 'TODO', 'REVIEW' ]:
        if word in tmp_content:
            return True

    return False

def needs_translation(content):

    tmp = content['changed'][0]['value']
    date_changed = datetime.strptime(tmp[0 : 10], '%Y-%m-%d').date()

    for key in [ "field_dept_translation_date", "field_gov_translation_date" ]:

        if content.get(key):

            tmp = content[key][0]['value']
            translation_date = datetime.strptime(tmp, '%Y-%m-%d').date()
            return translation_date < date_changed

    return True

def strip_html(content):

    begin = content.find("<")
    if begin == -1:
        return content

    end = content.find(">", begin + 1)
    if end == -1:
        return content

    new_content = content[0 : begin] + content[end + 1 : ]
    return strip_html(content=new_content)

def get_div(content, content_id):

    # Try to find the identifier
    id_pos = content.find(content_id)
    if id_pos == -1:
        pdb.set_trace()
        return []

    # Now try to find the beginning of the div containing it
    begin = content.rfind("<div", 0, id_pos)
    if begin == -1:
        pdb.set_trace()
        return []

    # Find end of <div tag
    content_begin = content.find(">", begin + 4)
    if content_begin == -1:
        pdb.set_trace()
        return []

    # Finally, try to find closing </div>
    end = content.find("</div>", content_begin + 1)
    if end == -1:
        pdb.set_trace()
        return []

    sub_string = content[content_begin + 1 : end]
    return [ sub_string ]

def do_export_faq_pair(faq_pair):

    target_id = faq_pair['target_id']

    url = "{}/rest/translation/paragraph/{}".format(server, target_id)

    response = requests.get(url + "?_format=json")
    if response.status_code != 200:
        report_err("url {} got status code {}".format(url, response.status_code), response.status_code)
        return;

    json = response.json()
    content = json[0]['bp_accordion_section']

    question = get_div(content=content, content_id="field--name-bp-accordion-section-title")
    answer = get_div(content=content, content_id="field--name-bp-text")

    if not question:
        # Somehow the question could not be parsed - this should never happen.
        pdb.set_trace()

    question = strip_html(content=question[0])

    if len(answer) == 1:
        answer = strip_html(content=answer[0])
    else:
        # We got unexpected # of answers:  try to handle this
        pdb.set_trace()

    return { "question": question, "answer": answer }

def do_export(url):

    auth_values = tuple(settings.CREDENTIALS['DETROITMI'].values())

    url = "{}{}".format(server, url)

    response = requests.get(url + "?_format=json", auth=HTTPBasicAuth(*auth_values))
    if response.status_code != 200:
        report_err("url {} got status code {}".format(url, response.status_code), response.status_code)
        return;

    data = response.json()

    if not needs_translation(data):
        return

    if in_review(data):
        report_err("url {} is still in REVIEW".format(url), "REVIEW status")
        return

    # Handle any faq pairs
    for idx, faq_pair in enumerate(data.get('field_faq_pair', [])):

        if faq_pair['target_type'] == 'paragraph':

            parsed_faq_pair = do_export_faq_pair(faq_pair=faq_pair)
            data['field_faq_pair'][idx].update(parsed_faq_pair)

        else:
            pdb.set_trace()

    print("url: " + url)

    print(json.dumps(data))
    export_cnt[url] = True
    print("")


if __name__ == '__main__':

    if len(sys.argv) == 2:
        output_errs = sys.argv[1] == '--debug=true'

    os.environ['DJANGO_SETTINGS_MODULE'] = 'django_apps.settings'
    django.setup()

    for url in urls:

        do_export(url=url)

    report_err_cnt()
