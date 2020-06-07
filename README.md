# GrabLinks

[![GitHub](https://img.shields.io/github/license/the-real-tokai/macuahuitl?color=green&label=License&style=flat)](https://github.com/the-real-tokai/grablinks/blob/master/LICENSE)
[![GitHub Code Size in Bytes](https://img.shields.io/github/languages/code-size/the-real-tokai/macuahuitl?label=Code%20Size&style=flat)](https://github.com/the-real-tokai/grablinks/)
[![Twitter Follow](https://img.shields.io/twitter/follow/binaryriot?color=blue&label=Follow%20%40binaryriot&style=flat)](https://twitter.com/binaryriot)

## Synopsis

`grablinks.py` is simple and streamlined Python 3 script to extract and filter links from a remote HTML resource.

## Requirements

An installation of `Python 3` (any version above v3.5 will do fine). Additionally the 3rd-party Python modules `requests`
and `beautifulsoup4` are required. Both modules can be easily installed with Pythons package manager `pip`, e.g.:

``` shell
pip --install requests --user
pip --install beautifulsoup4 --user
```

## Usage

```
usage: grablinks.py [-h] [-V] [-f FORMATSTR] [--fix-links] [-c CLASS]
                    [-s SEARCH] [-x REGEX]
                    URL

Extracts, and optionally filters, all links (`<a href=""/>') from a remote
HTML document.

positional arguments:
  URL                   a fully qualified URL to the source HTML document

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show version number and exit
  -f FORMATSTR, --format FORMATSTR
                        a format string to wrap in the output: %url% is
                        replaced by found URL entries; other supported
                        placeholders: %id%, %guid%, and %hash%
  --fix-links           try to convert relative and fragmental URLs to
                        absolute URLs (after filtering)

filter options:
  -c CLASS, --class CLASS
                        only extract URLs from href attributes of <a>nchor
                        elements with the specified class attribute content
  -s SEARCH, --search SEARCH
                        only output entries from the extracted result set, if
                        the search string occurs in the URL
  -x REGEX, --regex REGEX
                        only output entries from the extracted result set, if
                        the URL matches the regular expression
```

### Usage Examples

``` shell
# extract wikipedia links from 'www.example.com':
./grablinks.py 'https://www.example.com/ --search 'wikipedia'
https://ja.wikipedia.org/wiki/仲間由紀恵
https://ja.wikipedia.org/wiki/黒木華
https://ja.wikipedia.org/wiki/清野菜名
…
```

``` shell
# extract download links from 'www.example.com', create a shell script
# on-the-fly and pass it along to sh to fetch things with wget:
./grablinks.py 'https://www.example.com/ --search 'download.example.org' --format 'wget "%url%"' | sh
```

## History

<table>
    <tr>
        <td valign=top>1.1</td>
        <td valign=top nowrap>7-Jun-2020</td>
        <td>Initial public source code release</td>
    </tr>
</table>
