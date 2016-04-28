
import unittest
import httplib
import socket
import urllib2
import time
import sys
import datetime
import os
import pickle
from bs4 import BeautifulSoup

'''
# [Note to my future self]
# You can scrape an entire site for offline scraping with
# this command if needed:
 % wget --mirror --convert-links
    --adjust-extension --page-requisites --no-parent <site>
'''

class SiteScraper(object):

    def __init__(self, url, retries=0):

        if url is None or url == "":
            raise ValueError('url given to SiteScraper is Not valid')

        self.url = url
        self.retries = retries
        self.data = None
        self.debug = False
        self.testmode = False
        self.cache = {}
        self.maxCacheTime = datetime.timedelta(days=1)
        self.saveCacheDir = os.path.dirname(os.path.abspath(__file__)) + "/../data/cache/sites"
        self.cacheLoad()

    def cacheFileName(self):
        return self.saveCacheDir + "/" + self.url.rsplit('://',1)[-1].strip('/').replace('/','_') + "_scrape.pickle"

    def cacheSave(self):
        if not os.path.exists(os.path.dirname(self.cacheFileName())):
            os.makedirs(os.path.dirname(self.cacheFileName()))

        with open(self.cacheFileName(), 'wb') as handle:
            pickle.dump(self.cache, handle)

    def cacheLoad(self):
        if os.path.isfile(self.cacheFileName()):
            with open(self.cacheFileName(), 'rb') as handle:
                siteCache = pickle.load(handle)
                self.cache.update(siteCache)

    def scrape(self, urlOffset=None):

        if self.url is None:
            return None

        self.data = None

        url = self.url
        if urlOffset is not None:
            url = url + urlOffset

        if self.cache != None and url in self.cache and 'html' in self.cache[url] \
            and 'timestamp' in self.cache[url]:

            elapsedTimeInCache = datetime.datetime.now() - self.cache[url]['timestamp']
            if elapsedTimeInCache < self.maxCacheTime:
                html = self.cache[url]['html']
                soup = BeautifulSoup(html)
                self.data = soup
                return self.data

        retryCount = 0
        while True:
            error = False
            try:
                if self.debug:
                    print " SCRAPE: " + url
                hdr = {'User-Agent':'Mozilla/5.0'}
                request = urllib2.Request(url,headers=hdr)
                htmlFP = urllib2.urlopen(request)
                html = htmlFP.read()
            except (socket.error, httplib.BadStatusLine):
                time.sleep(0.4)
                error = True

            if not error:
                break
            if retryCount > self.retries:
                print >>sys.stderr, 'ERROR: site "' + self.url + '" is not responding'
                break

            retryCount = retryCount + 1

        if html is not None:
            soup = BeautifulSoup(html)
            self.data = soup
            if self.cache is not None:
                self.cache[url] = {'html':html, 'timestamp':datetime.datetime.now()}
                self.cacheSave()
            return self.data

        return self.data


    def scrapeTable(self, urlOffset=None, attrs={}, index=None):

        SiteScraper.scrape(self,urlOffset=urlOffset)

        if self.data is not None:
            if index is None:
                table = self.data.find('table', attrs=attrs)
            else:
                table = self.data.find_all('table', attrs=attrs)[index]

        self.data = None

        if table is None:
            return  self.data

        self.link = {}

        for link in table.findAll("a"):
            if link.has_attr('href'):
                self.link[link.text.strip()] = link['href']

        self.data = []

        for row in table.findAll("tr"):
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            self.data.append([ele for ele in cols])

        return self.data

class TestSiteScraper(unittest.TestCase):

    def testGoogle(self):
        s = SiteScraper("http://www.google.com")
        s.debug = True
        s.scrape()
        self.assertNotEquals(s.data,None)

        table = s.data.find('table')
        #print table
        self.assertNotEquals(table,None)

        linkList = []
        for link in s.data.findAll('a'):
            #print 'found an projectionsURL'
            if link.has_attr('href'):
                if link['href'][0] == '/':
                    linkList += [ s.url + link['href'] ]
                else:
                    linkList += [ link['href'] ]

        #print linkList
        #print len(linkList)
        self.assertGreaterEqual(len(linkList),10)


    def testTable(self):
        s = SiteScraper("http://www.html.am/html-codes/tables/")
        s.debug = True
        s.scrape()
        s.scrape()
        self.assertNotEquals(s.data,None)

        table = s.data.find('table', {'class': 'example'})
        #print table
        self.assertNotEquals(table,None)

        s.scrapeTable(attrs={'class': 'example'})
        print s.data



if __name__ == '__main__':
    unittest.main()