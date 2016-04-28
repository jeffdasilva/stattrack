
import unittest
import httplib
import socket
import urllib2
import time
import sys
import datetime
import os
import json
from bs4 import BeautifulSoup


class SiteScraper(object):

    def __init__(self, url, retries=0):
        '''
        Constructor
        '''

        if url is None:
            raise ValueError('URL given to SiteScraper is None')

        self.url = url
        self.data = None
        self.retries = retries
        self.debug = False
        self.cache = {}
        self.maxCacheTime = datetime.timedelta(days=1)
        self.saveCacheDir = os.path.dirname(os.path.abspath(__file__)) + "/../data/cache/sites"
        #self.loadCache()

    def cacheFile(self):
        return self.saveCacheDir + "/" + self.url.rsplit('://',1)[-1].strip('/').replace('/','_') + "_scrape.json"

    def saveCache(self):
        if not os.path.exists(os.path.dirname(self.cacheFile())):
            os.makedirs(os.path.dirname(self.cacheFile()))

        with open(self.cacheFile(), 'wb') as handle:
            json.dump(self.cache, handle)

    def loadCache(self):
        if os.path.isfile(self.cacheFile()):
            with open(self.cacheFile(), 'rb') as handle:
                siteCache = json.load(handle)
                self.update(siteCache)

    def scrape(self, urlOffset=None):

        if self.url is None:
            return None

        self.data = None

        url = self.url
        if urlOffset is not None:
            url = url + urlOffset

        if self.cache != None and url in self.cache and 'soup' in self.cache[url] \
            and 'timestamp' in self.cache[url]:

            elapsedTimeInCache = datetime.datetime.now() - self.cache[url]['timestamp']
            if elapsedTimeInCache < self.maxCacheTime:
                self.data = self.cache[url]['soup']
                return self.data

        retryCount = 0
        while True:
            error = False
            try:
                if self.debug:
                    print " SCRAPE: " + url
                hdr = {'User-Agent':'Mozilla/5.0'}
                request = urllib2.Request(url,headers=hdr)
                html = urllib2.urlopen(request)
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
            self.data = BeautifulSoup(html)
            if self.cache is not None:
                self.cache[url] = {'soup':self.data, 'timestamp':datetime.datetime.now()}
                #self.saveCache()
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