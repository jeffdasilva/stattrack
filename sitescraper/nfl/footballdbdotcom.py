import unittest
from sitescraper.scraper import SiteScraper

class FootballDBDotComScraper(SiteScraper):

    def __init__(self):
        super(SiteScraper, self).__init__()
        #self.url = "http://www.footballdb.com"
        self.url = "http://www.footballdb.com" + "/players/current.html?pos=QB"

        print self.url


class TestMyFantasyLeagueDotComScraper(unittest.TestCase):

    def testFootballDBDotComScraper(self):

        s = FootballDBDotComScraper()
        #"http://www.footballdb.com/players/current.html?pos=QB")
        #print s.url
        s.scrapeTable({'class':'statistics scrollable'})
        #s.scrape()

        print s.tableData
        print "done"


if __name__ == '__main__':
    unittest.main()

