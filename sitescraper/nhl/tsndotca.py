import datetime
import unittest

from sitescraper.scraper import SiteScraper


class TsnDotCaScraper(SiteScraper):

    Top300Stats = ["rank300", "name", "team", "position", "games", "goals", "assists", "points"]
    ByPositionStats = ["rankPosition", "name", "team", "games", "goals", "assists", "points", "plus-minus", "ppp", "pim", "hits", "blocks", "shotsOnGoal"]
    ByPositionGoalieStats = ["rankPosition", "name", "team", "games", "wins", "goalsAgainstAverage", "savePercentage", "shutouts"]

    def __init__(self):
        super(TsnDotCaScraper, self).__init__(url="http://www.tsn.ca")
        self.maxCacheTime = datetime.timedelta(days=1)

    def scrape(self, year=datetime.datetime.now().year):

        if str(year) == "2016":
            top300UrlOffset = "/crosby-no-1-in-the-top-300-projected-scorers-1.360216"
            byPositionOffset = "/fantasy-hockey-rankings-by-position-1.362639"
            tableAttrs={'class':'stats-table-scrollable article-table'}
        else:
            raise ValueError("projections for " + str(year) + " are not available yet")

        top300PlayerList = self.scrapeTable(urlOffset=top300UrlOffset,attrs=tableAttrs,index="RANK")

        self.players = []

        for player in top300PlayerList:
            if len(player) != len(TsnDotCaScraper.Top300Stats):
                continue
            self.players.append(dict(zip(TsnDotCaScraper.Top300Stats,player)))


        playerList = {}
        playerList['C'] = self.scrapeTable(urlOffset=byPositionOffset,attrs=tableAttrs,index=0)
        playerList['LW'] = self.scrapeTable(urlOffset=byPositionOffset,attrs=tableAttrs,index=1)
        playerList['RW'] = self.scrapeTable(urlOffset=byPositionOffset,attrs=tableAttrs,index=2)
        playerList['D'] = self.scrapeTable(urlOffset=byPositionOffset,attrs=tableAttrs,index=3)

        for position in playerList:
            for player in playerList[position]:
                if len(player) != len(TsnDotCaScraper.ByPositionStats):
                    continue
                self.players.append(dict(zip(TsnDotCaScraper.ByPositionStats,player)))
                self.players[-1]['position'] = position


        playerList['G'] = self.scrapeTable(urlOffset=byPositionOffset,attrs=tableAttrs,index=4)

        for goalie in playerList['G']:
            if len(goalie) != len(TsnDotCaScraper.ByPositionGoalieStats):
                continue
            self.players.append(dict(zip(TsnDotCaScraper.ByPositionGoalieStats,goalie)))
            self.players[-1]['position'] = 'G'

        self.data = self.players
        return self.players


class TestTsnDotCaScraper(unittest.TestCase):

    def testTsnDotCaScraper(self):

        s = TsnDotCaScraper()
        s.testmode = True
        data = s.scrape(year="2016")

        McDavidFound = 0

        for player in data:
            if str(player['name']) == "Connor McDavid":
                print player
                self.assertEqual(player['team'], "Edmonton")
                self.assertGreaterEqual(player['points'], 70)
                self.assertEqual(player['position'], 'C')
                McDavidFound += 1

        self.assertEquals(McDavidFound,2)

        raskFound = 0

        for player in data:
            if str(player['name']) == "Tuukka Rask":
                print player
                self.assertEqual(player['team'], "Boston")
                self.assertGreaterEqual(player['wins'], 35)
                self.assertGreaterEqual(player['savePercentage'], 0.925)
                self.assertEqual(player['position'], 'G')
                raskFound += 1

        self.assertEquals(raskFound,1)

