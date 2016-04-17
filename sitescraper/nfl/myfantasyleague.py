

import unittest
from sitescraper.scraper import SiteScraper

class MyFantasyLeagueDotComScraper(SiteScraper):

    def __init__(self):
        super(SiteScraper, self).__init__()
        self.url = "http://home.myfantasyleague.com"

class TestMyFantasyLeagueDotComScraper(unittest.TestCase):

    def testHomeScrape(self):
        s = MyFantasyLeagueDotComScraper()
        s.scrape()
        self.assertNotEquals(s.soup,None)
        #print s.soup

    def testOracleLeague(self):
        #http://www56.myfantasyleague.com/2016/home/43790
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()

