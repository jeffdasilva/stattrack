

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
                nameTeamPosition = row[3]

                if nameTeamPosition is None or nameTeamPosition == "":
                    continue
                elif nameTeamPosition == "Pre-Draft Selection Made":
                    continue
                elif nameTeamPosition.startswith("Waiting On "):
                    continue

                nameTeamPositionSplit = nameTeamPosition.rsplit(" ",1)
                if nameTeamPositionSplit[1][0] == '(':
                    nameTeamPosition = nameTeamPosition.rsplit(" ",1)[0]
                    nameTeamPositionSplit = nameTeamPosition.rsplit(" ",1)

                draftGridEntry = {}
                nameTeamSplit = nameTeamPosition.rsplit(" ",1)[0].rsplit(" ",1);
                nameSplit = nameTeamSplit[0].split(",",1)
                draftGridEntry['name'] = nameSplit[1].strip() + " " + nameSplit[0].strip()
                draftGridEntry['team'] = nameTeamSplit[1]
                draftGridEntry['position'] = nameTeamPositionSplit[1];
                draftGridEntry['owner'] = row[2]

                #self.draftGrid.append( ( name, team, position, owner ) )
                self.draftGrid.append( draftGridEntry )



class TestMyFantasyLeagueDotComScraper(unittest.TestCase):

    OracleLeagueID = 43790
    OracleLeagueYear = 2016

    def testOracleLeague(self):

        s = MyFantasyLeagueDotComScraper( TestMyFantasyLeagueDotComScraper.OracleLeagueID, \
                                          TestMyFantasyLeagueDotComScraper.OracleLeagueYear, \
                                          )
        s.scrape()
        #self.assertNotEquals(s.draftGrid,None)
        # site is down for maintenance
        self.assertEquals(s.draftGrid,None)

        #for p in s.draftGrid:
        #    print p

if __name__ == '__main__':
    unittest.main()

