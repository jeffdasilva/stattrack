import datetime
import unittest

from sitescraper.scraper import SiteScraper

class RotoWorldDotComScraper(SiteScraper):

    GamesPlayed = 'G'

    def __init__(self, league=None):
        super(RotoWorldDotComScraper, self).__init__(url="http://www.rotoworld.com")

        self.maxCacheTime = datetime.timedelta(days=30)
        #self.maxCacheTime = datetime.timedelta(days=4)0
        #self.maxCacheTime = datetime.timedelta(hours=1)

        self.league = league


    def scrape(self, playerName):

        # ToDo:
        # Steve johnson vs Stevie johnson (sd) vs steven johnson (pit) is an issue
        urlOffset = None

        if playerName == "Steve Smith":
            playerSearchString = "Smith Sr"
        elif playerName == "Javorius Allen":
            playerSearchString = "Allen,Buck"
        elif playerName == "Austin Seferian-Jenkins":
            playerSearchString = "Seferian-Jenkins"
        elif playerName == "Ben Roethlisberger":
            playerSearchString = "Roethlisberger"
        elif playerName == "Cam Newton":
            urlOffset = "/player/nfl/6491/cam-newton"
        elif playerName == "David Johnson":
            urlOffset = "/player/nfl/10404/david-johnson"
        elif playerName == "Alex Smith":
            urlOffset = "/player/nfl/3119/alex-smith"
        elif playerName == "Adrian Peterson":
            urlOffset = "/player/nfl/2491/adrian-peterson"
        elif playerName == "Brandon Marshall":
            urlOffset = "/player/nfl/3653/brandon-marshall"
        elif playerName == "Marvin Jones":
            urlOffset = "/player/nfl/7503/marvin-jones"
        elif playerName == "Jonathan Stewart":
            urlOffset = "/player/nfl/4650/jonathan-stewart"
        elif playerName == "Matt Jones":
            urlOffset = "/player/nfl/10493/matt-jones/1"
        elif playerName == "Zach Miller":
            urlOffset = "/player/nfl/5394/zach-miller"
        elif playerName == "Charles Clay":
            urlOffset = "/player/nfl/6681/charles-clay"
        elif playerName == "Ryan Griffin":
            urlOffset = "/player/nfl/8600/ryan-griffin"
        elif playerName == "Chris Thompson":
            urlOffset = "/player/nfl/8563/chris-thompson"
        elif playerName == "Josh Hill":
            urlOffset = "/player/nfl/8764/josh-hill"
        elif playerName == "Kevin White":
            urlOffset = "/player/nfl/10427/kevin-white"
        else:
            playerSearchString = playerName
            for suffix in [" Sr.", " Jr.", " III"]:
                if playerSearchString.endswith(suffix):
                    playerSearchString = playerSearchString.rsplit(suffix,1)[0]

            playerSearchString = str(playerSearchString.rsplit(' ',1)[1] + \
                ", " + playerSearchString.rsplit(' ',1)[0])

        if urlOffset is None:
            playerSearchString = playerSearchString.replace(' ','%20')
            urlOffset = "/content/playersearch.aspx?searchname=" + playerSearchString + "&sport=" + self.league.lower()


        playerDetails = self.scrapeTable(urlOffset=urlOffset, attrs={'id':'cp1_ctl00_tblPlayerDetails'})

        statsTable = self.scrapeTable(urlOffset=urlOffset, attrs={'class':'statstable'},index="Career Stats")
        if statsTable is None:
            print "No Rotoworld data found for " + playerName
            return None

        while len(statsTable) > 0 and len(statsTable[0]) == 0:
            statsTable = statsTable[1:]

        if len(statsTable) > 0:
            statCategories = statsTable[0]
            statsTable = statsTable[1:]
        else:
            print "No Rotoworld data found for " + playerName
            return None

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

        return stats

class TestRotoWorldDotComScraper(unittest.TestCase):

    def testRotoWorldDotComScraper(self):

        s = RotoWorldDotComScraper(league="nfl")
        s.testmode = True
        s.debug = True

        data = s.scrape(playerName="Eli Manning")
        self.assertNotEquals(data, None)
        self.assertGreater(int(data['2015']['G']),0)

        data = s.scrape(playerName="Tom Brady")
        self.assertNotEquals(data, None)
        self.assertGreater(int(data['2015']['G']),0)


        s.league = "nhl"
        data = s.scrape(playerName="Joe Thornton")
        self.assertNotEquals(data, None)

        s.league = "nfl"
        data = s.scrape(playerName="Odell Beckham Jr.")
        self.assertNotEquals(data, None)
        self.assertGreater(int(data['2015']['G']),0)

        data = s.scrape(playerName="Steve Smith")
        self.assertNotEquals(data, None)
        self.assertGreater(int(data['2015']['G']),0)

        data = s.scrape(playerName="Javorius Allen")
        self.assertNotEquals(data, None)
        self.assertGreater(int(data['2015']['G']),0)

        data = s.scrape(playerName="Cam Newton")
        self.assertNotEquals(data, None)
        self.assertEquals(int(data['2015']['G']),16)

        data = s.scrape(playerName="David Johnson")
        self.assertNotEquals(data, None)
        self.assertEquals(int(data['2015']['G']),16)

        data = s.scrape(playerName="Austin Seferian-Jenkins")
        print data
        self.assertNotEquals(data, None)

        s.cache = None
        for name in ["Ben Roethlisberger", "Adrian Peterson", "Alex Smith", "Brandon Marshall", \
                     "Marvin Jones", "Jonathan Stewart", "Matt Jones", "Zach Miller", "Charles Clay", \
                     "Ryan Griffin",  "Chris Thompson", "Josh Hill", "Kevin White"]:
            data = s.scrape(playerName=name)
            print data
            self.assertNotEquals(data, None)


if __name__ == '__main__':
    unittest.main()

