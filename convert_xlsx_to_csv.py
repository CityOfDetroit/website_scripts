#!/usr/bin/env python

import csv
import xlrd
import sys


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("usage:  ./convert_xlsx_to_csv.py <input file>")
        exit(1)

    input_file = sys.argv[1]

    wb = xlrd.open_workbook(input_file)
    sheet = wb.sheet_by_index(0)

    field_names = None
    writer = None

    for row_num in range(0, sheet.nrows):

        row = sheet.row(row_num)

        if not field_names:

            field_names = [ cell.value for cell in row ]
            writer = csv.DictWriter(sys.stdout, fieldnames=field_names, quoting=csv.QUOTE_ALL, dialect=csv.unix_dialect)
            writer.writeheader()

        else:

            cell_data = [ cell.value for cell in row ]
            row_data = { item[0] : item[1] for item  in zip(field_names, cell_data) }
            writer.writerow(row_data)
