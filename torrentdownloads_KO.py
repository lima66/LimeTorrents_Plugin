#VERSION: 1.00
#AUTHORS:lima66

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the author nor the names of its contributors may be
#      used to endorse or promote products derived from this software without
#      specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from xml.dom import minidom
from novaprinter import prettyPrinter
from helpers import retrieve_url, download_file


class torrentdownloads(object):
    url = "https://www.torrentdownloads.me"
    name = "TorrentDownloads"
    supported_categories = {'all': '0',
                            'music': '5',
                            'movies': '4',
                            'games': '3',
                            'software': '7',
                            'tv': '8',
                            'anime': '1',
                            'books': '2'}
    page_empty = 15800

    def download_torrent(self, info):
        print(download_file(info))

    def search(self, query, cat='all'):
        """ Performs search """
        cat_name = self.supported_categories.get(cat, None)
        if not cat_name:
            return

        # parser = self.MyHtmlParser(self.url)

        query = query.replace("%20", "+")
        """http://www.torrentdownloads.me4&search=john+wick"""
        """http://www.torrentdownloads.me/rss.xml?type=search&search=2017"""  # all
        """href="http://www.torrentdownloads.me/rss.xml?type=search&cid=4&search=2017"""  # category
        if cat == 'all':
            page = "".join((self.url, '/rss.xml?type=search&search={0}')).format(query)
        else:
            page = "".join((self.url, '/rss.xml?type=search&cid={0}&search={1}')).format(cat_name, query)

        """http://itorrents.org/torrent/F5CB6332E604E1B86A262EFF3D697D6E6945CFF8.torrent?title=john+wick+chapter+2+2017+ts+21oombkoshara+avi"""
        response = retrieve_url(page)
        response = response.replace('&', '&amp;')
        response = response.replace('\'', '&apos;')
        response = response.replace('<?xml version=&apos;1.0&apos; encoding=&apos;iso-8859-1&apos; ?>',
                                    "<?xml version='1.0' encoding='iso-8859-1' ?>")
        response = response.replace("<rss version=&apos;2.0&apos;>", "<rss version='2.0'>")
        # try:
        xmldoc = minidom.parseString(response)
        """except ExpatError as err:
            print(err)"""
        itemlist = xmldoc.getElementsByTagName('item')
        for item in itemlist:
            current_item = current_item = {"engine_url": self.url}
            current_item['name'] = item.getElementsByTagName('title')[0].childNodes[0].data
            current_item["link"] = "".join(('http://itorrents.org/torrent/',
                                            item.getElementsByTagName('info_hash')[0].childNodes[0].data,
                                            '.torrent?title=',item.getElementsByTagName('title')[0].childNodes[0]
                                            .data.replace(" ", "+").lower()))
            current_item["desc_link"] = "".join((self.url, item.getElementsByTagName('link')[0].childNodes[0].data))
            current_item["size"] = item.getElementsByTagName('size')[0].childNodes[0].data
            current_item["leech"] = item.getElementsByTagName('leechers')[0].childNodes[0].data
            if not current_item["leech"].isdigit():
                current_item["leech"] = ''
            current_item["seeds"] = item.getElementsByTagName('seeders')[0].childNodes[0].data
            if not current_item["seeds"].isdigit():
                current_item["seeds"] = ''

            prettyPrinter(current_item)

        return
