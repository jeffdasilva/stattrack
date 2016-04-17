

import unittest
import datetime
from sitescraper.scraper import SiteScraper

class MyFantasyLeagueDotComScraper(SiteScraper):

    def __init__(self, leagueID, year=datetime.datetime.now().year):
        super(SiteScraper, self).__init__()

        self.leagueID = leagueID
        self.year = year
        self.url = None


    def scrape(self):
        #url = "http://home.myfantasyleague.com"
        #url = "http://www56.myfantasyleague.com/" + str(year) + "/home/" + str(leagueID)

        url = "http://www56.myfantasyleague.com/" + str(self.year) + "/options?L=" + str(self.leagueID) + "&O=17"
        s = SiteScraper(url)
        s.scrapeTable({'class' : 'report nocaption'})

        if s.tableData is None:
            self.draftGrid = None
            return

        self.draftGrid = []

        for row in s.tableData:
            if len(row) > 3:
                player = row[3]

                if player is None or player == "":
                    continue
                elif player == "Pre-Draft Selection Made":
                    continue
                elif player.startswith("Waiting On "):
                    continue

                franchise = row[2]
                #print "franchise [" + franchise + "] selects: " + player

                self.draftGrid.append( ( player, franchise ) )



class TestMyFantasyLeagueDotComScraper(unittest.TestCase):

    OracleLeagueID = 43790
    OracleLeagueYear = 2016

    def testOracleLeague(self):

        s = MyFantasyLeagueDotComScraper( TestMyFantasyLeagueDotComScraper.OracleLeagueID, \
                                          TestMyFantasyLeagueDotComScraper.OracleLeagueYear, \
                                          )
        s.scrape()
        self.assertNotEquals(s.draftGrid,None)
        #print s.draftGrid

if __name__ == '__main__':
    unittest.main()

