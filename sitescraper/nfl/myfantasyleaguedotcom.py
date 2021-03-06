

import unittest
import datetime
from sitescraper.scraper import SiteScraper

class MyFantasyLeagueDotComScraper(SiteScraper):

    def __init__(self, leagueID, year=datetime.datetime.now().year):
        super(MyFantasyLeagueDotComScraper, self).__init__(url="http://www56.myfantasyleague.com")
        self.maxCacheTime = datetime.timedelta(seconds=30)
        #self.debug = True
        self.leagueID = leagueID
        self.year = year
        self.projectionsURL = None

    def scrape(self):

        urlOffset = "/" + str(self.year) + "/options?L=" + str(self.leagueID) + "&O=17"
        data = self.scrapeTable(urlOffset=urlOffset, attrs={'class' : 'report'})

        if data is None:
            self.draftGrid = None
            return None

        self.draftGrid = []

        data = data[1:]

        for row in data:
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
                draftGridEntry['isDrafted'] = True

                #self.draftGrid.append( ( name, team, position, owner ) )
                self.draftGrid.append( draftGridEntry )

        return self.draftGrid


class TestMyFantasyLeagueDotComScraper(unittest.TestCase):

    OracleLeagueID = 43790
    OracleLeagueYear = 2017

    def testOracleLeague(self):

        s = MyFantasyLeagueDotComScraper( TestMyFantasyLeagueDotComScraper.OracleLeagueID, \
                                          TestMyFantasyLeagueDotComScraper.OracleLeagueYear, \
                                          )
        #s.debug = True

        data = s.scrape()
        self.assertNotEquals(data,None)

        for p in s.draftGrid:
            print p

if __name__ == '__main__':
    unittest.main()

