import datetime
import unittest

from sitescraper.scraper import SiteScraper


class RotoWorldDotComScraper(SiteScraper):


    def __init__(self):
        super(RotoWorldDotComScraper, self).__init__(url="http://www.rotoworld.com")
        self.testmode = False

    def scrape(self):
        return {}


class TestRotoWorldDotComScraper(unittest.TestCase):

    def testRotoWorldDotComScraper(self):

        s = RotoWorldDotComScraper()
        s.testmode = True
        s.scrape()

if __name__ == '__main__':
    unittest.main()

