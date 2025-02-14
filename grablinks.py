#!/usr/bin/env python3
"""
	grablinks.py
	Extracts and filters links from a remote HTML document.

	Copyright © 2020-2025 Christian Rosentreter

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

	$Id: grablinks.py 33 2025-01-12 11:48:13Z tokai $
"""

__author__  = 'Christian Rosentreter'
__version__ = '1.10'
__all__     = []


import re
import argparse
import sys
import logging
import uuid
import hashlib
import urllib.parse
import posixpath
import platform
import os

# TODO: Kill off the 3rd-party dependencies? Python's own modules should be sufficient here…
try:
	import requests
	from bs4 import BeautifulSoup
except ImportError:
	print(('grablinks.py requires the Python modules `requests\' and `beautifulsoup4\'. Both modules '
		'can be installed with, e.g., `pip install requests beautifulsoup4 --user\''), file=sys.stderr)
	sys.exit(1)



def grab_links(url, insecure, tag, attribute, formatstr, fix_links, aclass, search, regex):
	"""This is where the magic happens…"""

	if url.startswith(('http://', 'https://')):
		params = {
			'timeout': 30,
			'headers': {
				'User-Agent': 'grablinks.py/{} (+https://github.com/the-real-tokai/grablinks)'.format(__version__),
			},
		}

		if insecure:
			import urllib3
			urllib3.disable_warnings()
			params['verify'] = False

		response    = requests.get(url, **params)
		loaded_data = response.content

		url = response.url  # update url, in case there was a redirection

	elif url.startswith('file://'):
		abspath = urllib.parse.unquote(url[7:])  # skip 'file://' and resolve percent encoding

		# Handle 'file-auth', see:  https://datatracker.ietf.org/doc/html/rfc8089
		nodename = platform.node()  # e.g.: foobar.local
		if abspath.startswith('localhost'):
			abspath = abspath[9:]
		elif abspath.startswith(nodename):
			abspath = abspath[len(nodename):]

		if not os.path.isabs(abspath):  # aka .startswith('/') on posix systems
			raise ValueError('Only absolute paths are supported in `file://\' protocol URLs.')

		# Note: open in binary mode; let 'html.parser' deal with the encoding…
		with open(abspath, 'rb') as fh:
			loaded_data = fh.read()

	else:
		raise ValueError('Unsupported protocol in URL.')


	uinfo = urllib.parse.urlsplit(url, scheme='https', allow_fragments=True)
	logging.debug(uinfo)


	soup  = BeautifulSoup(loaded_data, 'html.parser')

	if aclass is not None:
		# Make sure multiple classes can be found in any order, else --class 'foo bar' only
		# could match class="foo bar", but not class="bar foo".
		if ' ' in aclass:
			aclass = [s.strip() for s in aclass.split(' ')]
	else:
		# Just passing None to find_all's "class_" will skip "<a>"
		# tags w/o any class, not what we want…
		aclass = lambda c: True  # pylint: disable=unnecessary-lambda-assignment

	for link_id, link in enumerate(soup.find_all(tag, attrs={attribute: True}, class_=aclass)):
		furl = link[attribute]
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
							pass  # absolute, keep it as is
						else:
							p = uinfo.path
							if p[-1] != '/':  # last segment of input/ response URL seems to be a file
								p = posixpath.dirname(uinfo.path)
							tmp[2] = posixpath.join(p, tmp[2])
						if not parts.query:
							tmp[3] = uinfo.query
					furl = urllib.parse.urlunsplit(tmp)
					logging.debug('URL fixed into: %s', furl)
			except ValueError as e:
				logging.debug('extracted URL "%s" can\'t be fixed, passing it along as it is: %s', furl, e)

		if formatstr is not None:
			o = formatstr
			o = o.replace('%url%',  furl)
			o = o.replace('%id%',   str(link_id))
			o = o.replace('%guid%', str(uuid.uuid4()))
			o = o.replace('%hash%', hashlib.sha224(furl.encode('utf-8')).hexdigest())
			o = o.replace('%text%', link.text)
			print(o)
		else:
			print(furl)


def main():
	"""Preparing for liftoff…"""

	sys.tracebacklimit = 0
	#logging.basicConfig(level=logging.DEBUG)

	ap = argparse.ArgumentParser(
		description='Extracts, and optionally filters, links (`<a href=""/>\') from a remotely or locally stored HTML document.',
		epilog='Report bugs, request features, or provide suggestions via https://github.com/the-real-tokai/grablinks/issues'
	)

	ap.add_argument('-V', '--version', action='version',
		help="show version number and exit", version='%(prog)s {}'.format(__version__))
	ap.add_argument('url', type=str, metavar='URL',
		help='a fully qualified URL to the source HTML document')
	ap.add_argument('--insecure', action='store_true',
		help='disable verification of SSL/TLS certificates (e.g. to allow self-signed certificates)')
	ap.add_argument('-t', '--tag', type=str, metavar='TAG',
		help='extract from given tag (default: `a\'), also see `--attribute\'', default='a')
	ap.add_argument('-a', '--attribute', type=str, metavar='ATTRIBUTE',
		help='extract from given attribute (default: `href\'), also see `--tag\'', default='href')
	ap.add_argument('--images', action='store_true', help=argparse.SUPPRESS)  # (deprecated)
	ap.add_argument('-f', '--format', type=str, dest='formatstr',
		help=('a format string to wrap in the output: %%url%% is replaced by found URL entries; %%text%% is replaced '
			'with the text content of the link; other supported placeholders for generated values: %%id%%, %%guid%%, '
			'and %%hash%%'))
	ap.add_argument('--fix-links', action='store_true',
		help='try to convert relative and fragmental URLs to absolute URLs (after filtering)')

	g = ap.add_argument_group('additional filters')
	g.add_argument('-c', '--class', type=str, metavar='CLASS', dest='aclass',
		help='only extract URLs from href attributes of <a>nchor elements with the specified class attribute content. '
			'Multiple classes, separated by space, are evaluated with an logical OR, so any <a>nchor that has at least '
			'one of the classes will match.')
	g.add_argument('-s', '--search', type=str,
		help='only output entries from the extracted result set, if the search string occurs in the URL')
	g.add_argument('-x', '--regex', type=str,
		help='only output entries from the extracted result set, if the URL matches the regular expression')

	args = ap.parse_args()

	# Handle (deprecated) `--images' shortcut option
	if args.images:
		args.tag       = 'img'
		args.attribute = 'src'
	del args.images

	grab_links(**vars(args))


if __name__ == "__main__":
	main()
