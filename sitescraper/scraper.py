
import unittest
import httplib
import socket
import urllib2
import time
import sys
from bs4 import BeautifulSoup


class SiteScraper(object):

    def __init__(self, url=None, retries=0):
        '''
        Constructor
        '''
        self.url = url
        self.data = None
        self.retries = retries
        self.debug = False

    def scrape(self, urlOffset=None):

        if self.url is None:
            return None

        self.data = None

        url = self.url
        if urlOffset is not None:
            url = url + urlOffset

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
        s.scrape()
        self.assertNotEquals(s.data,None)

        table = s.data.find('table', {'class': 'example'})
        #print table
        self.assertNotEquals(table,None)

        s.scrapeTable(attrs={'class': 'example'})
        print s.data



if __name__ == '__main__':
    unittest.main()