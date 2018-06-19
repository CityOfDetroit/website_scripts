#!/usr/bin/env python

import os
import json
import sys


class WaterTestInfo():

    def __init__(self):

        self.name = ''
        self.path = ''
        self.status = ''
        self.fix_plan_path = ''
        self.fix_plan_status = ''

    def parse_url(line):
        """
        Parse url into path and status.
        """

        if "href" not in line:
            if 'Pending' == line:
                return '', 'Pending'
            else:
                return '', ''

        begin = 25
        end = line.find('"', begin)

        path = line[begin : end]

        begin = line.find('>', end)
        end = line.find('<', begin)

        status = line[begin + 1: end]

        return path, status

    def parse_status(line):

        begin = line.find('>')
        end = line.find('<', begin)

        if begin > 0 and end > 0:
            status = line[begin + 1 : end]
        else:
            status = line
        
        return status

    def add_val(self, line):

        if not self.name:
            self.name = line
        elif not self.path:

            # parse url
            self.path, tmp = WaterTestInfo.parse_url(line)

            # usually we throw away 'tmp', but sometimes there is no actually url (no report) if 
            # results are pending - in this case, store tmp as the status.
            if not self.path and tmp:
                self.status = tmp

        elif not self.status:
            self.status = WaterTestInfo.parse_status(line)
        else:

            # parse fix plan
            self.fix_plan_path, self.fix_plan_status = WaterTestInfo.parse_url(line)

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

    def get_json(self):

        return  {
            "name": self.name,
            "report_path": self.path,
            "status": self.status,
            "fix_plan_path": self.fix_plan_path,
            "fix_plan_status": self.fix_plan_status,
        }


def ignore_line(line):

    ignore_starts = [ "<table", "</table", "<thead", "</thead", "<tbody", "</tbody", ]
    for val in ignore_starts:
        if line.startswith(val):
            return True

    ignores = [ "<td>", "</td>" ]
    for val in ignores:
        if line == val:
            return True

    return False

def parse_lines(input_file):

    water_test_info = []
    first_item = True
    line_num = 0

    for line in input_file:

        line = line.lstrip().rstrip()
        line_num = line_num + 1

        if line == "<tr>":

            info = WaterTestInfo()

        elif line == "</tr>":

            if first_item:
                first_item = False
            else:
                if not info.is_complete():
                    raise Exception("info {} not complete (line num {}".format(info, line_num))

                # TODO remove "schools/" from beginning of path

                water_test_info.append(info)

        elif not ignore_line(line):

            info.add_val(line)


    return water_test_info


if __name__ == "__main__":

    if len(sys.argv) < 2:
        msg = "usage:  {} input_file\n(e.g., {} website_data/water_testing_dps.htm".format(sys.argv[0], sys.argv[0])
        raise Exception(msg)

    filename = sys.argv[1]
    with open(filename, newline='', encoding="utf8") as input_file:

        water_test_info = parse_lines(input_file)

    output = {
        "base_path": "/files/water_testing/",
        "locations": [ info.get_json() for info in water_test_info ]
    }

    print(json.dumps(output))
