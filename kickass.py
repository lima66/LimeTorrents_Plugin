#VERSION: 1.00
#AUTHORS:lima66


"""try:
    # python3
    from html.parser import HTMLParser
except ImportError:
   # python2
    from HTMLParser import HTMLParser"""
from html.parser import HTMLParser
from novaprinter import prettyPrinter
from helpers import retrieve_url, download_file
from re import compile as re_compile

class kickass(object):
    url = "https://kickass.cd"
    name = "KickAss"
    supported_categories = {'all': 'all',
                            'movies': 'movies',
                            'tv': 'tv',
                            'music': 'music',
                            'books': 'books',
                            'games': 'games',
                            'software': 'applications'}


    def download_torrent(self, info):
        print(download_file(info))

    class MyHtmlParser(HTMLParser):
        """ Sub-class for parsing results """
        def __init__(self, url):
            HTMLParser.__init__(self)
            self.url = url
            self.current_item = None #dict for found item
            self.item_name = None #key's name in current_item dict
            self.find_data = False
            self.counter = 0
            self.final_list = None
            self.table_found = False #table of torrent
            self. page_empty = 8856
            self.parser_class = {"nobr center": "size",  # class
                                 "green center": "seeds",
                                 "red lasttd center": "leech"}

        def handle_starttag(self, tag, attrs):
            if tag == "table":
                print("table")
            params = dict(attrs)
            if self.table_found:
                if tag == "td":
                    if "class" in params:
                        self.item_name = self.parser_class.get(params["class"], "")
                        if self.item_name:
                            self.find_data = True

            if self.table_found and tag == "a":
                if "href" in params:
                    link = params["href"]
                    if link.startswith("magnet:?"):
                        self.current_item["link"] = link
                        self.current_item["engine_url"] = self.url
                    elif link.endswith(".html"):
                        self.current_item["desc_link"] = self.url + link
                        self.item_name = "name"
                        self.find_data = True

            if params.get('class') == "data":
                self.table_found = True
                self.current_item = {}
                self.final_list = []

        def handle_data(self, data):
            if self.item_name and self.find_data:
                self.find_data = False
                self.current_item[self.item_name] = data.strip()

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
                    self.final_list = []
                    self.counter = 0

    def search(self, query, cat='all'):
        """ Performs search """
        #query = query.replace("%20", "%20")

        parser = self.MyHtmlParser(self.url)

        if cat == "all":
            #first page
            page = "".join((self.url, "/usearch/", query, "/"))
            html = retrieve_url(page)
            parser.feed(html)

            #Search more pages
            i = 2
            while i < 18:
                page = "{0}/usearch/{1}/{2}/".format(self.url, query, i)
                html = retrieve_url(page)
                lunghezza_html = len(html)
                if lunghezza_html <= parser.page_empty:
                   return

                parser.feed(html)
                i += 1
        else:
            # first page
            page = "".join((self.url, "/usearch/", query, "/"))
            html = retrieve_url(page)
            parser.feed(html)

            # Search more pages
            i = 1
            while i < 18:
                page = "{0}/usearch/{1}%20category:{2}/{3}/".format(self.url, query, self.supported_categories[cat], i)
                html = retrieve_url(page)
                lunghezza_html = len(html)
                if lunghezza_html <= parser.page_empty:
                    return

                parser.feed(html)
                i += 1

        parser.close()
