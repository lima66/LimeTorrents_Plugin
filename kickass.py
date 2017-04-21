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


class kickass(object):
    url = "https://katcr.co"
    name = "KickAss"

    all = [0]
    movies = [74, 149, 71, 80, 78, 79, 75, 81, 128, 148, 69, 150]
    tv = [5, 6, 41, 7, 146, 151, 152]
    music = [22, 23, 64, 65, 66, 67, 68, 129]
    books = [102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 132]
    games = [85, 87, 90, 91, 92, 97, 130]
    applications = [139, 140, 142, 144, 131]
    anime = [118, 133]
    others = [134, 136, 138, 145, 153, 154]

    supported_categories = {'all': all,
                            'movies': movies,
                            'tv': tv,
                            'music': music,
                            'books': books,
                            'games': games,
                            'software': applications,
                            'anime': anime,
                            'others': others}

    def download_torrent(self, info):
        print(download_file(info))

    class MyHtmlParser(HTMLParser):
        """ Sub-class for parsing results """
        A, TD, TR = ('a', 'td', 'tr')

        def __init__(self, url):
            HTMLParser.__init__(self)
            self.url = url
            self.current_item = {}  # dict for found item
            self.item_name = None  # key's name in current_item dict
            self.page_empty = 22000
            self.inside_tr = False
            self.find_data = False
            self.parser_class = {"ttable_col2": "size",  # class
                                 "green": "seeds",
                                 "#ff0000": "leech"}

        def handle_starttag(self, tag, attrs):
            params = dict(attrs)
            self.inside_tr = (self.inside_tr or tag == self.TR) and not params.get('class') == "ttable_head"
            if not self.inside_tr:
                return

            if self.inside_tr and (tag == self.TD or tag == 'font'):
                if "class" in params:
                    self.item_name = self.parser_class.get(params["class"], None)
                elif "color" in params:
                    self.item_name = self.parser_class.get(params["color"], None)

                if self.item_name:
                    self.find_data = True

            if "href" in params and params.get('class') == 'cellMainLink':
                link = params["href"]
                if tag == self.A and link.startswith('torrents-details.php'):
                    self.current_item["desc_link"] = "".join((self.url, "/new/", link))
                    self.current_item["engine_url"] = self.url
                    self.item_name = "name"
                    self.find_data = True

            elif "href" in params and params.get('title') == 'Download torrent file':
                link = params["href"]
                if tag == self.A and link.startswith('download.php?'):
                    self.current_item["link"] = "".join((self.url, "/new/", link))

            if tag == "tr" and params.get('class') == "t-row":
                self.current_item = {}

        def handle_data(self, data):
            if self.inside_tr and self.item_name and self.find_data:
                self.find_data = False
                self.current_item[self.item_name] = data.strip().replace(',', '')

        def handle_endtag(self, tag):
            if self.inside_tr and tag == self.TR:
                self.inside_tr = False
                self.item_name = None
                self.find_data = False
                array_length = len(self.current_item)
                if array_length < 1:
                    return
                prettyPrinter(self.current_item)
                self.current_item = {}

    def search(self, query, cat='all'):
        """ Performs search """
        parser = self.MyHtmlParser(self.url)

        query = query.replace("%20", "+")
        """https://katcr.co/new/torrents-search.php?cat=71&search=john&sort=seeders&order=desc&page=0"""

        array_category = self.supported_categories[cat]

        for category in array_category:
            number_page = 0
            while number_page < 15:
                page = "".join((self.url, "/new/torrents-search.php?cat={0}"
                                          "&search={1}&sort=seeders&order=desc&page={2}")).format(category, query,
                                                                                                  number_page)
                html = retrieve_url(page)
                length_html = len(html)
                if length_html <= parser.page_empty:
                    break

                parser.feed(html)
                number_page += 1

        parser.close()
