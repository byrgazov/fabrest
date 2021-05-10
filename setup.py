# -*- coding: utf-8 -*-

import os
import setuptools


HERE    = os.path.abspath(os.path.dirname(__file__))
SRCDIR  = os.path.join(HERE, 'src')
REQPATH = os.path.join(HERE, 'requires.txt')


requires = []

with open(REQPATH) as f:
	requires += [line.split('#', 1)[0].strip()
		for line in map(str.strip, f.readlines())
		if line and line.lstrip()[:1] != '#']


def setup():
	setuptools.setup(
		name         = 'fabrest',
		version      = '0.0.1',
		description  = 'Fabrique REST Application',
		author       = 'bw',
		author_email = 'bw@handsdriver.net',

		packages    = setuptools.find_packages(SRCDIR),
		package_dir = {'': os.path.basename(SRCDIR)},

		install_requires = requires,
		extras_require   = {},
		tests_require    = [],

		entry_points = {'console_scripts': []}
	)


if __name__ == '__main__':
	setup()
