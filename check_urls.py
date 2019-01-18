#!/usr/bin/env python

import requests
import sys
from requests.exceptions import ConnectionError


if __name__ == '__main__':

    filename = "urls.txt"
    missing_urls = set()
    missing_urls_list = []

    urls_checked = 0

    with open(filename) as file:
        for url in file:

            urls_checked = urls_checked + 1
            if urls_checked % 25 == 0:
                print("processed: {} urls".format(urls_checked))
                sys.stdout.flush()

            pos = url.find("detroitmi.gov")
            if pos < 0:
                path = url
            else:
                path = url[ pos + 13 : ].strip()

            url = "https://detroitmi.gov" + path.strip()

            try:
                response = requests.get(url)
                if response.status_code != 200:

                    missing_urls.add(path)
                    missing_urls_list.append(path)

            except ConnectionError as error:
                print("fatal error: " + str(error) + " - url: " + url)
            except:
                print("unknown error")

    tmp_domain = "detroitmi.gov"

    for url in missing_urls_list:
        print("https://" + tmp_domain + url)

    # for url in sorted(list(missing_urls)):
    #     print("http://" + tmp_domain + url)
