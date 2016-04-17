
import unittest
import urllib2
from bs4 import BeautifulSoup


class SiteScraper(object):

    def __init__(self, url=None):
        '''
        Constructor
        '''
        self.url = url
        self.soup = None

    def scrape(self):

        if self.url is None:
            self.soup = None
            return

        #f = urllib.urlopen(self.url)
        #html = f.read()

        request = urllib2.Request(self.url)
        html = urllib2.urlopen(request)

        self.soup = BeautifulSoup(html)

        #self.table = self.soup.find('table', {'id': 'data'})
        #self.table = self.soup.find('table')
#        for link in self.soup.findAll('a'):
#            print 'found an url'
#            if link.has_attr('href'):
#                print link['href']

class TestSiteScraper(unittest.TestCase):

    def testGoogle(self):
        s = SiteScraper("http://www.google.com")
        s.scrape()
        self.assertNotEquals(s.soup,None)
        #print s.soup

        table = s.soup.find('table')
        #print table
        self.assertNotEquals(table,None)

    def testTable(self):
        s = SiteScraper("http://www.html.am/html-codes/tables/")
        s.scrape()
        self.assertNotEquals(s.soup,None)
        #print s.soup

        table = s.soup.find('table', {'class': 'example'})
        #print table
        self.assertNotEquals(table,None)


if __name__ == '__main__':
    unittest.main()