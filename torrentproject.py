#VERSION: 1.00
#AUTHORS:lima66


try:
    # python3
    from html.parser import HTMLParser
except ImportError:
    # python2
    from HTMLParser import HTMLParser

from novaprinter import prettyPrinter
from helpers import retrieve_url, download_file
import re

DOWNLOAD_PATTERN = r'<a .* href=\'/(.*)\'>Download Torrent from torrentproject\.se</a>'

class torrentproject(object):
    url = "https://torrentproject.se"
    name = "TorrentProject"

    supported_categories = {'all': '9000',
                            'movies': '2000',
                            'tv': '2101',
                            'music': '1000',
                            'books': '3000',
                            'games': '6000',
                            'software': '7000',
                            'others': '4000'}
    page_empty = 0

    def download_torrent(self, info):
        torrent_page = retrieve_url(info)
        torrent_link_match = re.search(DOWNLOAD_PATTERN, torrent_page)
        if torrent_link_match and torrent_link_match.groups():
            clean_name = torrent_link_match.groups()[0].strip()
            torrent_file = self.url + clean_name
            print(download_file(torrent_file))
        else:
            print('')

    class MyHtmlParser(HTMLParser):
        """ Sub-class for parsing results """
        DIV, A, HREF, CLASS, SPAN, LI = ('div', 'a', 'href', 'class', 'span', 'li')

        def __init__(self, url):
            HTMLParser.__init__(self)
            self.url = url
            self.current_item = {}  # dict for found item
            self.item_name = None  # key's name in current_item dict
            self.inside_li = False
            self.find_data = False
            self.find_number = False
            self.parser_class = {"l tl": "name",  # class
                                 "bc torrent-size": "size",
                                 "bc seeders": "seeds",
                                 "bc leechers": "leech"}

        def handle_starttag(self, tag, attrs):
            params = dict(attrs)

            if tag == self.LI and self.CLASS in params:
                if params.get(self.CLASS) == 'g w0':
                    self.inside_li = True
            if not self.inside_li:
                return

            if self.CLASS in params:
                value_find = self.parser_class.get(params[self.CLASS], None)
                if value_find:
                    self.item_name = value_find
                    self.find_data = True
                    self.current_item[self.item_name] = ""

            if self.HREF in params and params.get(self.CLASS) == 'l tl':
                link = params[self.HREF]
                if tag == self.A and link.endswith('.html'):
                    self.current_item["desc_link"] = "".join((self.url, link))
                    self.current_item["link"] = "".join((self.url, link))
                    self.current_item["engine_url"] = self.url
                    self.find_data = True

            if tag == self.SPAN and self.CLASS in params:
                if params.get(self.CLASS) == "gac_b":
                    self.find_data = True

        def handle_data(self, data):
            if self.inside_li and self.item_name and self.find_data:
                self.find_data = False
                self.current_item[self.item_name] = data.strip().replace(',', '')

        def handle_endtag(self, tag):
            if self.inside_li and tag == self.LI:
                self.inside_li = False
                self.item_name = None
                self.find_data = False
                array_length = len(self.current_item)

                if array_length < 7:
                    return

                prettyPrinter(self.current_item)
                self.current_item = {}

    def search(self, query, cat='9000'):
        """ Performs search """
        parser = self.MyHtmlParser(self.url)

        query = query.replace("%20", "+")
        """http://torrentproject.se/?hl=en&safe=off&num=20&start=0&orderby=seeders&s=2017&filter=9000"""

        category = self.supported_categories[cat]
        number_page = 0
        while True:
            page = "".join((self.url, "/?hl=en&safe=off&num=20&start={0}"
                                      "&orderby=seeders&s={1}&filter={2}")).format(number_page, query, category)

            html = retrieve_url(page)
            length_html = len(html)
            if length_html <= self.page_empty:
                break

            parser.feed(html)
            parser.close()

            number_page += 1


