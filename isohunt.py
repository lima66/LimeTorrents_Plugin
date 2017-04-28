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

DOWNLOAD_PATTERN = r'<a href="https://torrent.isohunt.to/download.php?(.*)" class="btn btn-lg btn-warning btn-download" (.*)>'

class isohunt(object):
    url = "https://isohunt.to"
    name = "IsoHunt"

    supported_categories = {'all': '0',
                            'movies': '5',
                            'tv': '8',
                            'music': '6',
                            'books': '9',
                            'games': '3',
                            'software': '2',
                            'anime': '1',
                            'others': '7'}
    page_empty = 29900

    def download_torrent(self, info):
        if info.startswith("http"):
            torrent_page = retrieve_url(info)
            torrent_link_match = re.search(DOWNLOAD_PATTERN, torrent_page)
            if torrent_link_match and torrent_link_match.groups():
                clean_name = torrent_link_match.groups()[0].split('title')[0].replace('"', '').strip()
                torrent_file = 'https://torrent.isohunt.to/download.php' + clean_name
                print(download_file(torrent_file))
            else:
                print('')
        else:
            print(download_file(info))

    class MyHtmlParser(HTMLParser):
        """ Sub-class for parsing results """
        A, TD, TR = ('a', 'td', 'tr')

        def __init__(self, url):
            HTMLParser.__init__(self)
            self.url = url
            self.current_item = {}  # dict for found item
            self.item_name = None  # key's name in current_item dict
            self.inside_tr = False
            self.inside_td = False
            self.find_data = False
            self.end_pages = False
            self.parser_class = {"title-row": "name",  # class
                                 "size-row": "size",
                                 "sy": "seeds",
                                 "sn": "seeds"}
            self.tr_cont = 0

        def handle_starttag(self, tag, attrs):
            params = dict(attrs)

            if tag == 'li':
                if 'class' in params:
                    if params.get('class') == 'next disabled':
                        self.end_pages = True

            if 'data-key' in params:
                if tag == self.TR and params.get('data-key') == str(self.tr_cont):
                    self.inside_tr = True
                    self.current_item = {}
            if not self.inside_tr:
                return

            if self.inside_tr and tag == self.TD and params.get('class') == 'title-row':
                self.inside_td = True

            if self.inside_tr and tag == self.TD:
                if "class" in params:
                    self.item_name = self.parser_class.get(params["class"], None)
                    if self.item_name:
                        self.find_data = True

            if "href" in params and self.inside_td:
                link = params["href"]
                if tag == self.A and link.startswith('/torrent_details'):
                    self.current_item["desc_link"] = "".join((self.url, link))
                    self.current_item["engine_url"] = self.url
                    self.current_item["link"] = self.current_item["desc_link"]
                    self.item_name = "name"
                    self.find_data = True

        def handle_data(self, data):
            if self.inside_tr and self.item_name and self.find_data:
                self.find_data = False
                self.current_item[self.item_name] = data.strip().replace(',', '')

        def handle_endtag(self, tag):
            if self.inside_tr and self.inside_td and tag == self.TD:
                self.inside_td = False

            if self.inside_tr and tag == self.TR:
                self.current_item["leech"] = '-1'
                self.inside_tr = False
                self.item_name = None
                self.find_data = False
                array_length = len(self.current_item)
                if array_length < 7:
                    return
                prettyPrinter(self.current_item)
                self.current_item = {}
                self.tr_cont += 1

    def search(self, query, cat='0'):
        """ Performs search """
        parser = self.MyHtmlParser(self.url)

        query = query.replace("%20", "+")
        """https://isohunt.to/torrents/?iht=5&ihq=2017&Torrent_page=40"""

        category = self.supported_categories[cat]

        number_page = 0
        while True:
            if category == '0':
                page = "".join((self.url, "/torrents/?ihq={0}&Torrent_page={1}&Torrent_sort=-seeders")).format(
                    query, number_page)
            else:
                page = "".join((self.url, "/torrents/?iht={0}&ihq={1}&Torrent_page={2}&Torrent_sort=-seeders")).format(
                    category, query, number_page)

            html = retrieve_url(page)
            parser.feed(html)
            parser.close()
            if parser.end_pages:
                return
            parser.tr_cont = 0
            number_page += 40


