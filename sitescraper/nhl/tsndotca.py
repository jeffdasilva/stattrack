import datetime
import unittest

from sitescraper.scraper import SiteScraper


class TsnDotCaScraper(SiteScraper):

    # FYI - don't trust tsn's listed team because it could be out of date
    Top300Stats = ["tsn.top300.rank", "name", "tsn.top300.team",
                   "position", "tsn.top300.games", "tsn.top300.goals", \
                   "tsn.top300.assists", "tsn.top300.points"]

    ByPositionStats = ["tsn.by_pos.rank", "name", "tsn.by_pos.team", \
                       "tsn.by_pos.games", "tsn.by_pos.goals", "tsn.by_pos.assists", \
                       "tsn.by_pos.points", "tsn.by_pos.plus-minus", "tsn.by_pos.ppp", \
                       "tsn.by_pos.pim", "tsn.by_pos.hits", "tsn.by_pos.blocks", \
                       "tsn.by_pos.shotsOnGoal"]

    # FYI - older version included shutouts and new versions sadly do not :(
    ByPositionGoalieStats = ["tsn.by_pos.rank", "name", "tsn.by_pos.team", \
                             "tsn.by_pos.games", "tsn.by_pos.wins", \
                             "tsn.by_pos.goalsAgainstAverage", \
                             "tsn.by_pos.savePercentage"]
    def __init__(self):
        super(TsnDotCaScraper, self).__init__(url="http://www.tsn.ca")
        self.maxCacheTime = datetime.timedelta(days=1)
        #self.maxCacheTime = datetime.timedelta(seconds=5)

    def scrape(self, year=datetime.datetime.now().year):

        if str(year) == "2016":
            #top_300_tsn_version_string = "1.360216"
            top_300_tsn_version_string = "1.565371"

            #by_position_tsn_version_string = "1.362639"
            by_position_tsn_version_string = "1.566798"

            top300UrlOffset = "/crosby-leads-list-of-top-300-projected-scorers-" + top_300_tsn_version_string

            byPositionOffset = "/fantasy-hockey-rankings-by-position-" + by_position_tsn_version_string
            tableAttrs={'class':'stats-table-scrollable article-table'}

        else:
            raise ValueError("projections for " + str(year) + " are not available yet")

        top300PlayerList = self.scrapeTable(urlOffset=top300UrlOffset,attrs=tableAttrs,index="RANK")

        self.players = []

        for player in top300PlayerList:
            if len(player) != len(TsnDotCaScraper.Top300Stats):
                continue
            self.players.append(dict(zip(TsnDotCaScraper.Top300Stats,player)))
            #print self.players[-1]['name']

        if self.debug:
            print "Number of players found: " + str(len(self.players))
            assert(len(self.players)==300)

        playerList = {}
        playerList['C'] = self.scrapeTable(urlOffset=byPositionOffset,attrs=tableAttrs,index=0)
        playerList['LW'] = self.scrapeTable(urlOffset=byPositionOffset,attrs=tableAttrs,index=1)
        playerList['RW'] = self.scrapeTable(urlOffset=byPositionOffset,attrs=tableAttrs,index=2)
        playerList['D'] = self.scrapeTable(urlOffset=byPositionOffset,attrs=tableAttrs,index=3)

        for position in playerList:
            for player in playerList[position]:
                if len(player) != len(TsnDotCaScraper.ByPositionStats):
                    if self.debug and len(player) > 0:
                        print player
                        raise ValueError("Something is wrong here with Player Stats!")
                    continue
                self.players.append(dict(zip(TsnDotCaScraper.ByPositionStats,player)))
                self.players[-1]['position'] = position


        playerList['G'] = self.scrapeTable(urlOffset=byPositionOffset,attrs=tableAttrs,index=4)

        if self.debug:
            for pos in playerList:
                assert(len(playerList[pos])>=50)

        for goalie in playerList['G']:
            if len(goalie) != len(TsnDotCaScraper.ByPositionGoalieStats):
                if self.debug and len(goalie) > 0:
                    print goalie
                    raise ValueError("Something is wrong here with Goalie Stats!")
                continue
            self.players.append(dict(zip(TsnDotCaScraper.ByPositionGoalieStats,goalie)))
            self.players[-1]['position'] = 'G'

        return self.players


class TestTsnDotCaScraper(unittest.TestCase):

    def testTsnDotCaScraper(self):

        s = TsnDotCaScraper()
        s.testmode = True
        s.debug = True
        data = s.scrape(year="2016")

        McDavidFound = 0

        for player in data:
            #print player['name']
            if str(player['name']) == "Connor McDavid":
                if 'tsn.top300.team' in player:
                    self.assertEqual(player['tsn.top300.team'], "Edmonton")
                    self.assertGreaterEqual(player['tsn.top300.points'], 70)
                    self.assertEqual(player['position'], 'C')
                else:
                    self.assertEqual(player['tsn.by_pos.team'], "Edmonton")
                    self.assertGreaterEqual(player['tsn.by_pos.points'], 70)
                    self.assertEqual(player['position'], 'C')

                McDavidFound += 1

        self.assertEquals(McDavidFound,2)

        raskFound = 0

        for player in data:
            if str(player['name']) == "Tuukka Rask":
                self.assertEqual(player['tsn.by_pos.team'], "Boston")
                self.assertGreaterEqual(player['tsn.by_pos.wins'], 35)
                self.assertGreaterEqual(player['tsn.by_pos.savePercentage'], 0.925)
                self.assertEqual(player['position'], 'G')
                raskFound += 1

        self.assertEquals(raskFound,1)

