

import unittest
import datetime
from sitescraper.scraper import SiteScraper

class MyFantasyLeagueDotComScraper(SiteScraper):

    def __init__(self, id, year=datetime.datetime.now().year):
        super(SiteScraper, self).__init__()

        self.id = id
        self.year = year
        self.url = None


    def scrape(self):
        #url = "http://home.myfantasyleague.com"
        #url = "http://www56.myfantasyleague.com/" + str(year) + "/home/" + str(id)

        url = "http://www56.myfantasyleague.com/" + str(self.year) + "/options?L=" + str(self.id) + "&O=17"
        s = SiteScraper(url)
        s.scrape()
        self.soup = s.soup


class TestMyFantasyLeagueDotComScraper(unittest.TestCase):

    def testHomeScrape(self):
        s = MyFantasyLeagueDotComScraper(43970,2016)
        s.scrape()
        self.assertNotEquals(s.soup,None)
        #print s.soup

    def testOracleLeague(self):

        s = MyFantasyLeagueDotComScraper(43790,2016)
        s.scrape()
        self.assertNotEquals(s.soup,None)
        print s.soup

        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()

