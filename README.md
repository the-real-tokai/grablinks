# GrabLinks

[![GitHub](https://img.shields.io/github/license/the-real-tokai/grablinks?color=green&label=License&style=flat)](https://github.com/the-real-tokai/grablinks/blob/master/LICENSE)
[![GitHub Code Size in Bytes](https://img.shields.io/github/languages/code-size/the-real-tokai/grablinks?label=Code%20Size&style=flat)](https://github.com/the-real-tokai/grablinks/)
[![Mastodon Follow](https://img.shields.io/badge/mastodon-follow?id=109326414755382704&server=https://social.anoxinon.de&color=blue&label=Follow %40binaryriot&style=flat)](https://social.anoxinon.de/@binaryriot)
[![Twitter Follow](https://img.shields.io/twitter/follow/binaryriot?color=blue&label=Follow%20%40binaryriot&style=flat)](https://twitter.com/binaryriot)

## Synopsis

`grablinks.py` is a simple and streamlined Python 3 script to extract and filter links from a remote HTML resource.

## Requirements

An installation of `Python 3` (any version above `3.5` should do fine). Additionally the 3rd-party Python modules `requests`
and `beautifulsoup4` are required. Both modules can be easily installed with Python's package manager `pip`, e.g.:

``` shell
pip --install requests --user
pip --install beautifulsoup4 --user
```

## Usage

```
usage: grablinks.py [-h] [-V] [--insecure] [-f FORMATSTR] [--fix-links]
                    [--images] [-c CLASS] [-s SEARCH] [-x REGEX]
                    URL

Extracts, and optionally filters, all links (`<a href=""/>') from a remote
HTML document.

positional arguments:
  URL                   a fully qualified URL to the source HTML document

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show version number and exit
  --insecure            disable verification of SSL/TLS certificates (e.g. to
                        allow self-signed certificates)
  -f FORMATSTR, --format FORMATSTR
                        a format string to wrap in the output: %url% is
                        replaced by found URL entries; %text% is replaced with
                        the text content of the link; other supported
                        placeholders for generated values: %id%, %guid%, and
                        %hash%
  --fix-links           try to convert relative and fragmental URLs to
                        absolute URLs (after filtering)
  --images              extract `<img src=""/>' instead `<a href=""/>'.

filter options:
  -c CLASS, --class CLASS
                        only extract URLs from href attributes of <a>nchor
                        elements with the specified class attribute content.
                        Multiple classes, separated by space, are evaluated
                        with an logical OR, so any <a>nchor that has at least
                        one of the classes will match.
  -s SEARCH, --search SEARCH
                        only output entries from the extracted result set, if
                        the search string occurs in the URL
  -x REGEX, --regex REGEX
                        only output entries from the extracted result set, if
                        the URL matches the regular expression

Report bugs, request features, or provide suggestions via
https://github.com/the-real-tokai/grablinks/issues
```

### Usage Examples

```shell
# extract wikipedia links from 'www.example.com':
$ grablinks.py 'https://www.example.com/' --search 'wikipedia'
https://ja.wikipedia.org/wiki/仲間由紀恵
https://ja.wikipedia.org/wiki/黒木華
https://ja.wikipedia.org/wiki/清野菜名
…
```

```shell
# extract download links from 'www.example.com', create a shell script
# on-the-fly and pass it along to sh to fetch things with wget:
$ grablinks.py 'https://www.example.com/' --search 'download.example.org' --format 'wget "%url%"' | sh
# Note: Do not do that at home. It is dangerous! 😱
```

```shell
# alternatively just pass to wget directly:
$ grablinks.py 'https://www.example.com/' --search 'download.example.org' | sort -u | wget -i-
```

```shell
# extract/ handle links like
# <a href="https://example.com/a-cryptic-ID">proper-filename.ext</a>
$ grablinks.py 'https://www.example.com/' --format 'wget '\''%url%'\'' -O '\''%text%'\' > fetchfiles.sh
$ sh fetchfiles.sh
# Note: %text% is not sanitized by grablinks.py for safe shell usage. It is
#       recommended to verify this before executing things automatically
```

## History

<table>
	<tr>
		<td valign=top>1.8</td>
		<td valign=top nowrap>21-Nov-2024</td>
		<td>Added support for "&lt;img src=&quot;&quot;&gt;" via '--images'.</td>
	</tr>
	<tr>
		<td valign=top>1.7</td>
		<td valign=top nowrap>21-Jan-2024</td>
		<td>
			Disable urllib3 warnings when '--insecure' is used.
		</td>
	</tr>
	<tr>
		<td valign=top>1.6</td>
		<td valign=top nowrap>2-Dec-2023</td>
		<td>
			Added '--insecure' argument to disable SSL/TLS certificate verification<br>
			Added support for '%text%' placeholder in format string (&lt;a&gt;text&lt;/a&gt;)
		</td>
	</tr>
	<tr>
		<td valign=top>1.5</td>
		<td valign=top nowrap>24-Nov-2022</td>
		<td>Added a (fixed) timeout to the remote request.</td>
	</tr>
	<tr>
		<td valign=top>1.4</td>
		<td valign=top nowrap>30-May-2022</td>
		<td>Improved handling of passing multiple classes to '--class'.</td>
	</tr>
	<tr>
		<td valign=top>1.3</td>
		<td valign=top nowrap>6-Feb-2021</td>
		<td>Fix: handling of common edge cases when '--fix-links' is used.</td>
	</tr>
	<tr>
		<td valign=top>1.2</td>
		<td valign=top nowrap>16-Aug-2020</td>
		<td>Fix: in some cases links from "&lt;a&gt;" tags without a 'class' attribute were not part of the result.</td>
	</tr>
	<tr>
		<td valign=top>1.1</td>
		<td valign=top nowrap>7-Jun-2020</td>
		<td>Initial public source code release</td>
	</tr>
</table>
