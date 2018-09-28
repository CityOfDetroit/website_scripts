#!/usr/bin/env python

import sys

import load_translation


if __name__ == '__main__':

	with open('bn_reload.txt') as url_list:

		for url in url_list:

			url = url[37 : ].strip()

			filename = 'translated_content/bn/' + url.replace('/', '%2F') + '.txt'

			try:

				file = open(filename)

			except:

				print(filename + " not found")
				continue

			print("loading " + filename)

			load_translation.Loader().run(lang='bn', filename=filename)
