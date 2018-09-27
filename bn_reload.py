#!/usr/bin/env python

import sys

import load_translations


import pdb


if __name__ == '__main__':

	if len(sys.argv) < 2:
		raise Exception('usage: bn_reload.py url')


	pdb.set_trace()


	url = sys.argv[1]
	url = url[37 : ]

	filename = 'translated_content/bn/' + url.replace('/', '%2F') + '.txt'

	print(filename)

	load_translations.Loader().run(lang='bn', filename=filename)