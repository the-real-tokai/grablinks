#!/usr/bin/env python3
"""
	grablinks.py
	Extracts and filters links from a remote HTML document.

	Copyright © 2020-2022 Christian Rosentreter

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <https://www.gnu.org/licenses/>.

	$Id: grablinks.py 17 2022-05-30 04:09:01Z tokai $
"""

__author__  = 'Christian Rosentreter'
__version__ = '1.4'
__all__     = []


import re
import argparse
import sys
import logging
import uuid
import hashlib
import urllib

# TODO: Kill off the 3rd-party dependencies? Python's own modules should be sufficient here…
try:
	import requests
	from bs4 import BeautifulSoup
except ImportError as e:
	print(('grablinks.py requires the Python modules `requests\' and `beautifulsoup4\'. Both modules '
		'can be installed with, e.g., `pip install requests beautifulsoup4 --user\''), file=sys.stderr)
	sys.exit(1)



def grab_links(url, search, regex, formatstr, aclass, fix_links):
	"""This is where the magic happens…"""

	uinfo = urllib.parse.urlsplit(url, scheme='https', allow_fragments=True)
	req   = requests.get(url)
	soup  = BeautifulSoup(req.text, "html.parser")

	found_urls = 0

	if aclass is not None:
		# Make sure multiple classes can be found in any order, else --class 'foo bar' only
		# could match class="foo bar", but not class="bar foo".
		if ' ' in aclass:
			aclass = [s.strip() for s in aclass.split(' ')]
	else:
		# Just passing None to find_all's "class_" will skip "<a>"
		# tags w/o any class, not what we want…
		aclass = lambda c: True

	for link in soup.find_all('a', href=True, class_=aclass):
		furl = link['href']
		logging.debug('URL extracted: %s', furl)

		if (search is not None) and (furl.find(search) is -1):
			logging.debug('extracted URL "%s" doesn\'t contain user search string "%s", skip.', furl, search)
			continue

		if (regex is not None) and (not re.match(regex, furl)):
			logging.debug('extracted URL "%s" doesn\'t match user regex "%s", skip.', furl, regex)
			continue

		if fix_links:
			try:
				parts = urllib.parse.urlsplit(furl, allow_fragments=True)
				logging.debug(parts)

				if not parts.scheme:
					tmp = list(parts)  # tuple(scheme, netloc, path, query, fragment)
					tmp[0] = uinfo.scheme
					if not parts.netloc:
						tmp[1] = uinfo.netloc
						if not parts.path:
							tmp[2] = uinfo.path
						elif tmp[2][0] == '/':
							pass  # keep it as is
						else:
							tmp[2] = uinfo.path + ('/' if uinfo.path[-1] != '/' else '') + tmp[2]
						if not parts.query:
							tmp[3] = uinfo.query
					furl = urllib.parse.urlunsplit(tmp)
					logging.debug('URL fixed into: %s', furl)
			except ValueError as e:
				logging.debug('extracted URL "%s" can\'t be fixed, passing it along as it is: %s', furl, e)

		found_urls += 1

		if formatstr is not None:
			o = formatstr
			o = o.replace('%url%',  furl)
			o = o.replace('%id%',   str(found_urls))
			o = o.replace('%guid%', str(uuid.uuid4()))
			o = o.replace('%hash%', hashlib.sha224(furl.encode('utf-8')).hexdigest())
			print(o)
		else:
			print(furl)


def main():
	"""Preparing for liftoff…"""

	sys.tracebacklimit = 0
	# logging.basicConfig(level=logging.DEBUG)

	ap = argparse.ArgumentParser(
		description='Extracts, and optionally filters, all links (`<a href=""/>\') from a remote HTML document.',
		epilog='Report bugs, request features, or provide suggestions via https://github.com/the-real-tokai/grablinks/issues'
	)

	ap.add_argument('-V', '--version', action='version',
		help="show version number and exit", version='%(prog)s {}'.format(__version__))
	ap.add_argument('url', type=str, metavar='URL',
		help='a fully qualified URL to the source HTML document')
	ap.add_argument('-f', '--format', type=str, dest='formatstr',
		help=('a format string to wrap in the output: %%url%% is replaced by found URL entries; other supported '
			'placeholders: %%id%%, %%guid%%, and %%hash%%'))
	ap.add_argument('--fix-links', action='store_true',
		help='try to convert relative and fragmental URLs to absolute URLs (after filtering)')

	g = ap.add_argument_group('filter options')
	g.add_argument('-c', '--class', type=str, metavar='CLASS', dest='aclass',
		help='only extract URLs from href attributes of <a>nchor elements with the specified class attribute content. Multiple classes, separated by space, are evaluated with an logical OR, so any <a>nchor that has at least one of the classes will match.')
	g.add_argument('-s', '--search', type=str,
		help='only output entries from the extracted result set, if the search string occurs in the URL')
	g.add_argument('-x', '--regex', type=str,
		help='only output entries from the extracted result set, if the URL matches the regular expression')

	grab_links(**vars(ap.parse_args()))


if __name__ == "__main__":
	main()
