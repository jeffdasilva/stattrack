
'''
# [Note to my future self]
# You can scrape an entire site for offline scraping with
# this command if needed:
 % wget --mirror --convert-links
    --adjust-extension --page-requisites --no-parent <site>
'''

from bs4 import BeautifulSoup
import cookielib
import datetime
import httplib
from multiprocessing.pool import ThreadPool
import os
import pickle
import socket
import sys
from threading import Lock
import time
import unittest
import urllib2


class SiteScraper(object):

    def __init__(self, url, retries=0):

        if url is None or url == "":
            raise ValueError('url given to SiteScraper is Not valid')

        self.url = url
        self.retries = retries
        self.debug = False
        self.verbose = True
        self.testmode = False
        self.cache = {}
        self.cacheSaveEnabled = True
        self.maxCacheTime = datetime.timedelta(days=1)
        self.cookiefile = None

        self.cacheLock = Lock()
        self.saveCacheDir = os.path.dirname(os.path.abspath(__file__)) + "/../data/cache/sites"
        self.cacheLoad()

    def cacheFileName(self):
        return self.saveCacheDir + "/" + self.url.rsplit('://',1)[-1].strip('/').replace('/','_') + "_scrape.pickle"

    def cacheSave(self):
        if self.cache is None or not self.cacheSaveEnabled:
            return

        #lock is done by caller
        #self.cacheLock.acquire()
        try:
            if not os.path.exists(os.path.dirname(self.cacheFileName())):
                os.makedirs(os.path.dirname(self.cacheFileName()))

            with open(self.cacheFileName(), 'wb') as handle:
                pickle.dump(self.cache, handle)
        finally:
            pass
            #self.cacheLock.release()

    def cacheLoad(self):
        if self.cache is None:
            return

        self.cacheLock.acquire()
        try:
            if os.path.isfile(self.cacheFileName()):
                with open(self.cacheFileName(), 'rb') as handle:
                    siteCache = pickle.load(handle)
                    self.cache.update(siteCache)
        finally:
            self.cacheLock.release()


    def scrape(self, urlOffset=None):

        if self.url is None:
            return None

        data = None

        url = self.url
        if urlOffset is not None:
            url = url + urlOffset
        url = url.strip()

        if self.cache != None:
            self.cacheLock.acquire()
            try:
                if url in self.cache and 'html' in self.cache[url]:
                    if 'timestamp' in self.cache[url]:
                        elapsedTimeInCache = datetime.datetime.now() - self.cache[url]['timestamp']
                        if elapsedTimeInCache < self.maxCacheTime:
                            if self.debug: print " [Cache Hit] " + url
                            html = self.cache[url]['html']
                            soup = BeautifulSoup(html, "lxml")
                            data = soup
                            return data
                        else:
                            if self.debug:
                                print " [Cache Expired] " + url
                                print "   Timestamp is:           " + str(self.cache[url]['timestamp'])
                                print "   Elapsed time in cache: " + str(elapsedTimeInCache)
                                print "   Max time in cache:     " + str(self.maxCacheTime)
                    else:
                        if self.debug: print " [Cache Miss with No Timestamp] " + url
                else:
                    if self.debug: print " [Cache Miss] " + url
            finally:
                self.cacheLock.release()
        else:
            if self.debug: print " [Cache Disabled] " + url

        retryCount = 0
        while True:
            error = False
            try:
                if self.debug or self.verbose: print " [SCRAPE] " + url
                hdr = {'User-Agent':'Mozilla/5.0'}

                if self.cookiefile is not None:
                    cj = cookielib.MozillaCookieJar(self.cookiefile)
                    cj.load()
                    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
                    urllib2.install_opener(opener)

                proxy = os.environ.get('HTTP_PROXY')
                if proxy is not None:
                    if self.debug: print "   [DEBUG] HTTP_PROXY set to " + proxy

                request = urllib2.Request(url,headers=hdr)
                if self.debug: print "   [DEBUG] urllib2.Request() - Done"

                htmlFP = urllib2.urlopen(request, timeout=30)
                if self.debug: print "   [DEBUG] urllib2.urlopen() - Done"

                html = htmlFP.read()
            except (socket.error, httplib.BadStatusLine, urllib2.HTTPError, httplib.IncompleteRead):
                time.sleep(0.4)
                error = True

            if error:
                if self.debug: print " [SCRAPE ERROR] " + url

            if not error and html is not None:
                soup = BeautifulSoup(html, "lxml")
                data = soup
                if self.cache is not None:
                    self.cacheLock.acquire()
                    try:
                        if self.debug: print " [Cache Updated] " + url
                        self.cache[url] = {'html':html, 'timestamp':datetime.datetime.now()}
                        self.cacheSave()
                        if self.debug: print "   Timestamp is:           " + str(self.cache[url]['timestamp'])
                    finally:
                        self.cacheLock.release()
                break
            else:
                if self.debug: print " [SCRAPE returned no html] " + url

            if retryCount >= self.retries:
                print >>sys.stderr, 'ERROR: site "' + url + '" is not responding'
                break

            retryCount = retryCount + 1

        return data

    def scrapeTables(self, urlOffset=None, attrs={}):

        data = SiteScraper.scrape(self,urlOffset=urlOffset)

        if data is not None:
            tableList = data.find_all('table', attrs=attrs)

        data = []

        if tableList is not None:
            for tbl in tableList:
                tblEntry = []
                for row in tbl.findAll("tr"):
                    cols = row.find_all('td')
                    cols = [ele.text.strip() for ele in cols]
                    tblEntry.append([ele for ele in cols])
                data.append(tblEntry)

        return data

    def scrapeTable(self, urlOffset=None, attrs={}, index=None):

        data = SiteScraper.scrape(self,urlOffset=urlOffset)

        table = None
        if data is not None:
            if index is None:
                table = data.find('table', attrs=attrs)
            elif isinstance(index, int):
                tableList = data.find_all('table', attrs=attrs)
                table = tableList[index]
            elif isinstance(index, str):
                tableList = data.find_all('table', attrs=attrs)
                for t in tableList:
                    firstRow = t.find("tr")
                    if index in str(firstRow):
                        table = t
                        break
            else:
                raise ValueError('index value is invalid: ' + index)

        data = None

        if table is None:
            return data

        data = []

        for row in table.findAll("tr"):
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols])

        return data

    def scrapeLinks(self, urlOffset=None, attrs={}):

        data = SiteScraper.scrape(self,urlOffset=urlOffset)

        link = {}
        for link_found in data.findAll("a", attrs=attrs):
            if link_found.has_attr('href'):
                link[link_found.text.strip()] = link_found['href']

        return link

    def scrapeWithThreadPool(self,func,iterable,numOfThreads):

        if numOfThreads == 0:
            result = []
            for i in iterable:
                result.append(func(i))
        else:
            self.cacheSaveEnabled = False
            try:
                pool = ThreadPool(numOfThreads)
                result = pool.map(func,iterable)
                pool.close()
                pool.join()
            finally:
                self.cacheSaveEnabled = True

            self.cacheLock.acquire()
            try:
                self.cacheSave()
            finally:
                self.cacheLock.release()



        return result



class TestSiteScraper(unittest.TestCase):

    def testGoogle(self):
        s = SiteScraper("http://www.google.com")
        s.debug = True
        data = s.scrape()
        self.assertNotEquals(data,None)

        table = data.find('table')
        #print table
        self.assertNotEquals(table,None)

        linkList = []
        for link in data.findAll('a'):
            #print 'found an projectionsURL'
            if link.has_attr('href'):
                if link['href'][0] == '/':
                    linkList += [ s.url + link['href'] ]
                else:
                    linkList += [ link['href'] ]

        #print linkList
        #print len(linkList)
        self.assertGreaterEqual(len(linkList),10)

        l = s.scrapeLinks()
        self.assertGreaterEqual(len(l),10)
        #print l

    def testTable(self):
        s = SiteScraper("http://www.html.am/html-codes/tables/")
        s.debug = True
        s.scrape()
        data = s.scrape()
        self.assertNotEquals(data,None)

        table = data.find('table', {'class': 'example'})
        #print table
        self.assertNotEquals(table,None)

        data = s.scrapeTable(attrs={'class': 'example'})
        print data

        s.cache = None
        data = s.scrape()
        self.assertNotEquals(data,None)

if __name__ == '__main__':
    unittest.main()
