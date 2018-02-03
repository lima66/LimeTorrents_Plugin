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


class ilcorsaronero(object):
    url = "http://ilcorsaronero.info"
    name = "IlCorsaroNero"

    movies = [19, 1, 20]
    tv = [15]
    music = [2, 18]
    books = [6]
    games = [3, 13, 14]
    applications = [7]
    anime = [5]

    supported_categories = {'movies': movies,
                            'tv': tv,
                            'music': music,
                            'books': books,
                            'games': games,
                            'software': applications,
                            'anime': anime}

    def download_torrent(self, info):
        print(download_file(info))

    class MyHtmlParser(HTMLParser):
        """ Sub-class for parsing results """

        A, TD, TR, HREF, INPUT = ('a', 'td', 'tr', 'href', 'input')

        def __init__(self, url):
            HTMLParser.__init__(self)
            self.url = url
            self.current_item = {}  # dict for found item
            self.item_name = None  # key's name in current_item dict
            self.page_empty = 9200
            self.inside_tr = False
            self.inside_td = False
            self.find_data = False
            self.parser_class = {"#FF6600": "size",  # class
                                 "#00CC00": "seeds",
                                 "#0066CC": "leech",
                                 "#CCCCCC": "empty"}

        def handle_starttag(self, tag, attrs):
            params = dict(attrs)

            if tag == self.TR and (params.get('class') == 'odd' or params.get('class') == 'odd2'):
                self.inside_tr = True
                self.current_item = {}
            if not self.inside_tr:
                return

            if self.inside_tr and tag == self.TD:
                self.inside_td = True

            if self.inside_tr and self.inside_td:
                if "color" in params:
                    self.item_name = self.parser_class.get(params["color"], None)
                    if self.item_name:
                        self.find_data = True
                        if not self.item_name == "empty":
                            self.current_item[self.item_name] = " "

            if self.inside_tr and self.inside_td and self.HREF in params and params.get('class') == 'tab':
                link = params["href"]
                if tag == self.A and link.startswith('http://ilcorsaronero.info/tor/'):
                    self.current_item["desc_link"] = link
                    self.current_item["engine_url"] = self.url
                    self.item_name = "name"
                    self.find_data = True

                """http://itorrents.org/torrent/F37ED38F8A13218E5ABE56CFEA97E173C57C087E.torrent"""
            if self.inside_tr and self.inside_td and tag == self.INPUT and params.get('class') == 'downarrow':
                self.current_item['link'] = ''.join(('http://itorrents.org/torrent/', params.get('value'), '.torrent'))

        def handle_data(self, data):
            if self.inside_tr and self.item_name and self.find_data:
                if self.item_name == "empty":
                    self.current_item["seeds"] = '-1'
                    self.current_item["leech"] = '-1'
                    self.item_name = None
                    self.find_data = False
                else:
                    self.find_data = False
                    self.current_item[self.item_name] = data.strip().replace(',', '')

        def handle_endtag(self, tag):
            if self.inside_tr and tag == self.TD:
                self.inside_td = False

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

        """http://ilcorsaronero.info/advsearch.php?categoty=19&search=2017+md&&order=data&by=DESC&page=1"""
        """http://ilcorsaronero.info/torrent-ita/2/2016%20%20mina.html"""
        """http://ilcorsaronero.info/advsearch.php?&category=1&search=2016+bdrip&&order=data&by=DESC&page=1"""
        if cat == 'all':
            query = query.replace("%20", "+")
            number_page = 0
            while number_page < 15:
                page = "".join((self.url, "/advsearch.php?search={0}&&order=data&by=DESC&page={1}")).format(query, number_page)
                html = retrieve_url(page)
                length_html = len(html)
                if length_html <= parser.page_empty:
                    return

                parser.feed(html)
                number_page += 1
        else:
            array_category = self.supported_categories[cat]
            for category in array_category:
                number_page = 0
                while number_page < 15:
                    page = "".join((self.url, "/advsearch.php?&category={0}&search={1}&&order=data&by=DESC&page={2}")).format(category, query, number_page)
                    html = retrieve_url(page)
                    length_html = len(html)
                    if length_html <= 14500:
                        break

                    parser.feed(html)
                    number_page += 1

        parser.close()
