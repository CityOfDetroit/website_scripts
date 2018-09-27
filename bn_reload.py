#!/usr/bin/env python

import sys

import load_translation


if __name__ == '__main__':

	if len(sys.argv) < 2:
		raise Exception('usage: bn_reload.py url')

	url = sys.argv[1]
	url = url[37 : ]

	filename = 'translated_content/bn/' + url.replace('/', '%2F') + '.txt'

	print(filename)

	load_translation.Loader().run(lang='bn', filename=filename)
