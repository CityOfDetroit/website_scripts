#!/usr/bin/env python

import requests
import sys
from requests.exceptions import ConnectionError


if __name__ == '__main__':

    filename = "urls.txt"
    # filename = "urls_to_translate.txt"
    missing_urls = set()

    with open(filename) as file:
        for url in file:

            pos = url.find("detroitmi.gov")
            if pos < 0:
                break

            path = url[ pos + 13 : ].strip()
            url = "http://detroitmi.theneighborhoods.org" + path

            try:
                response = requests.get(url)
                if response.status_code != 200:

                    missing_urls.add(path)

                    count = len(missing_urls)
                    if count % 10 == 0:
                        print("percent finished: {}%".format(count / 942 * 100))
                        sys.stdout.flush()

            except ConnectionError as error:
                print("fatal error: " + str(error) + " - url: " + url)
            except:
                print("unknown error")

    tmp_domain = "detroitmi.theneighborhoods.org"

    for url in sorted(list(missing_urls)):
        print("http://" + tmp_domain + url)
