import datetime
import unittest

from sitescraper.scraper import SiteScraper

class RotoWorldDotComScraper(SiteScraper):

    GamesPlayed = 'G'

    def __init__(self):
        super(RotoWorldDotComScraper, self).__init__(url="http://www.rotoworld.com")
        self.maxCacheTime = datetime.timedelta(days=90)

    def scrape(self, playerName, league):

        # ToDo:
        # Steve johnson vs Stevie johnson (sd) vs steven johnson (pit) is an issue

        if playerName == "Steve Smith":
            playerSearchString = "Smith Sr"
        elif playerName == "Javorius Allen":
            playerSearchString = "Allen,Buck"
        elif playerName == "Austin Seferian-Jenkins":
            playerSearchString = "Seferian-Jenkins"
        else:
            playerSearchString = playerName
            for suffix in [" Sr.", " Jr.", " III"]:
                if playerSearchString.endswith(suffix):
                    playerSearchString = playerSearchString.rsplit(suffix,1)[0]

            playerSearchString = str(playerSearchString.rsplit(' ',1)[1] + \
                ", " + playerSearchString.rsplit(' ',1)[0])

        playerSearchString = playerSearchString.replace(' ','%20')
        urlOffset = "/content/playersearch.aspx?searchname=" + playerSearchString + "&sport=" + league.lower()
        self.scrapeTable(urlOffset=urlOffset, attrs={'id':'cp1_ctl00_tblPlayerDetails'})
        playerDetails = self.data
        #print playerDetails

        # ToDo: Need to improve this
        # There are lots of statstable classes in this page so we're really getting luck if this works
        # I think this only works in the offseason. When in season, the "this season" statstabe table shows up first
        self.scrapeTable(urlOffset=urlOffset, attrs={'class':'statstable'})
        if self.data is None:
            return self.data

        statsTable = self.data

        while len(statsTable) > 0 and len(statsTable[0]) == 0:
            statsTable = statsTable[1:]

        if len(statsTable) > 0:
            statCategories = statsTable[0]
            statsTable = statsTable[1:]
        else:
            self.data = None
            return self.data

        #print statsTable

        stats = []
        for data in statsTable:
            d = dict(zip(statCategories,data))
            stats.append(d)

        stats = {'name':playerName}
        if playerDetails is not None:
            stats['rotoworld'] = playerDetails
        for yearData in statsTable:
            d = dict(zip(statCategories,yearData))
            if 'Year' in d:
                year = d['Year']
                del d['Year']
                stats[year] = {}
                stats[year] = d

        self.data = stats
        return self.data


class TestRotoWorldDotComScraper(unittest.TestCase):

    def testRotoWorldDotComScraper(self):

        s = RotoWorldDotComScraper()
        s.testmode = True

        s.scrape(playerName="Eli Manning", league="nfl")
        self.assertNotEquals(s.data, None)
        self.assertGreater(int(s.data['2015']['G']),0)

        s.scrape(playerName="Tom Brady", league="nfl")
        self.assertNotEquals(s.data, None)
        self.assertGreater(int(s.data['2015']['G']),0)

        s.scrape(playerName="Joe Thornton", league="nhl")
        self.assertNotEquals(s.data, None)

        s.scrape(playerName="Odell Beckham Jr.", league="nfl")
        self.assertNotEquals(s.data, None)
        self.assertGreater(int(s.data['2015']['G']),0)

        s.scrape(playerName="Steve Smith", league="nfl")
        self.assertNotEquals(s.data, None)
        self.assertGreater(int(s.data['2015']['G']),0)

        s.scrape(playerName="Javorius Allen", league="nfl")
        self.assertNotEquals(s.data, None)
        self.assertGreater(int(s.data['2015']['G']),0)

        s.cache = None
        s.scrape(playerName="Austin Seferian-Jenkins", league="nfl")
        print s.data
        self.assertNotEquals(s.data, None)



if __name__ == '__main__':
    unittest.main()

