
import urllib.request, urllib.parse, urllib.error
import re

from bs4 import BeautifulSoup
import requests

from tvoverlord.util import U
from tvoverlord.config import Config


class Provider (object):

    provider_urls = [
        'http://thepiratebay.se',
        'http://thepiratebay.org',
    ]

    name = 'The Pirate Bay'

    @staticmethod
    def se_ep(show_title, season, episode):
        search_one = '%s S%sE%s' % (
            show_title,
            season.rjust(2, '0'),
            episode.rjust(2, '0'))

        search_two = '%s %sx%s' % (
            show_title,
            season,
            episode.rjust(2, '0'))

        return [search_one, search_two]


    def search(self, search_string, season=False, episode=False):

        show_data = []

        if season and episode:
            searches = self.se_ep(search_string, season, episode)
        else:
            searches = [search_string]

        for try_url in self.provider_urls:
            urls = '%s/search/ ' % try_url
            for search in searches:
                pretty_name = search_string
                search_string = urllib.parse.quote(search)
                url = '%s/search/%s/0/7/0' % (try_url, search_string)
                urls += '%s/0/7/0 ' % search_string
                #print('>', url)
                try:
                    r = requests.get(url)
                except requests.exceptions.ConnectionError:
                    # if can't connect, go to the next url
                    continue
                html = r.content
                soup = BeautifulSoup(html, 'lxml')

                search_results = soup.find('table', id='searchResult')
                if not search_results:
                    continue

                # for each row in search results table, (skipping thead)
                for tr in search_results.find_all('tr')[1:]:

                    date = 'unknown'
                    size = 'unknown'
                    seeds = 0

                    tds = tr.find_all('td')[1:]
                    name = tds[0].find('a', {'class':'detLink'}).string

                    # when searching using 'nondbshow', sometimes the last
                    # tr gets mangled.  All that can be extracted is the
                    # torrent name and magnet url.  This only happends
                    # when using BeautifulSoup, not a browser.
                    try:
                        details = tds[0].find('font').contents[0].split(', ')
                        date = details[0].replace('Uploaded ', '')
                        size = details[1].replace('Size ', '').replace('MiB', 'MB').replace('GiB', 'GB')
                        seeds = tds[1].string
                    except IndexError:
                        # sometimes some fields are empty, so trying to
                        # access them throws an IndexError.  We can safely
                        # skip them.
                        pass

                    magnet = tds[0].find('a', href=re.compile('magnet:.*')).attrs['href']

                    show_data.append([name, size, date, seeds, 'PB', magnet])

            return show_data

        return show_data


if __name__ == '__main__':

    pass