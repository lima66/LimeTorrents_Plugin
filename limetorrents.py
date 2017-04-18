#VERSION: 3.00
#AUTHORS: Douman (custparasite@gmx.se)
#CONTRIBUTORS: Diego de las Heras (ngosang@hotmail.es)

from novaprinter import prettyPrinter
from helpers import retrieve_url, download_file
from re import compile as re_compile
from html.parser import HTMLParser

class limetorrents(object):
    url = "https://www.limetorrents.cc"
    name = "LimeTorrents"
    supported_categories = {'all'      : 'all',
                            'anime'    : 'anime',
                            'software' : 'applications',
                            'games'    : 'games',
                            'movies'   : 'movies',
                            'music'    : 'music',
                            'tv'       : 'tv',
                            'other'    : 'other'}

    def download_torrent(self, info):
        print(download_file(info))

    class MyHtmlParser(HTMLParser):
        """ Sub-class for parsing results """
        def __init__(self, url):
            HTMLParser.__init__(self)
            self.url = url
            self.current_item = None #dict for found item
            self.item_name = None #key's name in current_item dict
            self.counter = 0
            self.final_list = None
            self.table_found = False #table of torrent
            self.parser_class = {"tdnormal": "size",  # class
                                 "tdseed": "seeds",
                                 "tdleech": "leech"}

        def handle_starttag(self, tag, attrs):
            params = dict(attrs)
            if self.table_found:
                if tag == "td":
                    if "class" in params:
                        self.item_name = self.parser_class.get(params["class"], None)
                        if self.item_name:
                            self.current_item[self.item_name] = ""

            if self.table_found and tag == "a":
                if "href" in params:
                    link = params["href"]
                    if link.startswith("http://itorrents.org/torrent/"):
                        self.current_item["desc_link"] = link.split('=')[1]
                        self.current_item["link"] = link
                        self.current_item["engine_url"] = self.url
                        self.item_name = "name"

            if params.get('class') == "table2":
                self.table_found = True
                self.current_item = {}
                self.final_list = []

        def handle_data(self, data):
            if self.item_name:
                self.current_item[self.item_name] = data
                if self.item_name == "leech":
                    if self.current_item:
                        self.final_list.insert(self.counter, self.current_item)
                        self.current_item = {}
                        self.counter += 1

        def handle_endtag(self, tag):
                if self.table_found and tag == "table":
                    self.table_found = False
                    self.item_name = None
                    for items in self.final_list:
                        prettyPrinter(items)
                    self.current_item = {}
                    self.counter = 0

    def search(self, query, cat='all'):
        """ Performs search """
        query = query.replace("%20", "-")

        parser = self.MyHtmlParser(self.url)
        page = "".join((self.url, "/search/", self.supported_categories[cat], "/", query, "/"))

        html = retrieve_url(page)
        parser.feed(html)

        additional_pages = re_compile("/search/{0}/{1}/date/[0-9]+".format(self.supported_categories[cat], query))
        list_searches = additional_pages.findall(html)[:-1] #last link is next(i.e. second)
        for page in map(lambda link: "".join((self.url, link)), list_searches):
            html = retrieve_url(page)
            parser.feed(html)
        parser.close()
