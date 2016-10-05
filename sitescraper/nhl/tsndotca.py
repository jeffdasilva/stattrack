import datetime
import unittest

from db.player.strings import HockeyPlayerStrings
from sitescraper.scraper import SiteScraper


class TsnDotCaScraper(SiteScraper):

    esByPos = HockeyPlayerStrings('tsn.by_pos')
    esTop300 = HockeyPlayerStrings('tsn.top300')

    # FYI - don't trust tsn's listed team because it could be out of date
    Top300Stats = [esTop300.projectedString('rank'),
                   esTop300.name(),
                   esTop300.statString('team'),
                   esTop300.position(),
                   esTop300.projectedGamesPlayed(),
                   esTop300.projectedGoals(),
                   esTop300.projectedAssists(),
                   esTop300.projectedPoints()
                   ]

    ByPositionStats = [esByPos.projectedString('rank'),
                       esByPos.name(),
                       esByPos.statString('team'),
                       esByPos.projectedGamesPlayed(),
                       esByPos.projectedGoals(),
                       esByPos.projectedAssists(),
                       esByPos.projectedPoints(),
                       esByPos.projectedString('plus-minus'),
                       esByPos.projectedString('ppp'),
                       esByPos.projectedString('pim'),
                       esByPos.projectedString('hits'),
                       esByPos.projectedString('blocks'),
                       esByPos.projectedString('shotsOnGoal')
                       ]

    ByPositionGoalieStats = [esByPos.projectedString('rank'),
                             esByPos.name(),
                             esByPos.statString('team'),
                             esByPos.projectedGamesPlayed(),
                             esByPos.projectedWins(),
                             esByPos.projectedString('goalsAgainstAverage'),
                             esByPos.projectedString('savePercentage')
                             ]

    ProjectedGamesPlayed = [esTop300.projectedGamesPlayed(), esByPos.projectedGamesPlayed()]
    ProjectedGoals = [esTop300.projectedGoals(), esByPos.projectedGoals()]
    ProjectedAssists = [esTop300.projectedAssists(), esByPos.projectedAssists()]
    ProjectedWins = [ esByPos.projectedWins() ]
    ProjectedTies = []
    ProjectedShutouts = []

    def __init__(self):
        super(TsnDotCaScraper, self).__init__(url="http://www.tsn.ca")
        self.maxCacheTime = datetime.timedelta(days=1)
        #self.maxCacheTime = datetime.timedelta(seconds=5)

    def scrape(self, year=datetime.datetime.now().year):

        # scrape Scott Cullen's projections

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

        #top300PlayerListHeader = top300PlayerList[0]
        top300PlayerList = top300PlayerList[1:]

        self.players = []

        for player in top300PlayerList:
            if len(player) != len(TsnDotCaScraper.Top300Stats):
                continue
            self.players.append(dict(zip(TsnDotCaScraper.Top300Stats,player)))
            self.players[-1]['scraper'] = [TsnDotCaScraper.esTop300.prefix]
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

            playerList[position] = playerList[position][1:]

            for player in playerList[position]:
                if len(player) != len(TsnDotCaScraper.ByPositionStats):
                    if self.debug and len(player) > 0:
                        print player
                        raise ValueError("Something is wrong here with Player Stats!")
                    continue
                self.players.append(dict(zip(TsnDotCaScraper.ByPositionStats,player)))
                self.players[-1]['position'] = position
                self.players[-1]['scraper'] = [TsnDotCaScraper.esByPos.prefix]

        playerList['G'] = self.scrapeTable(urlOffset=byPositionOffset,attrs=tableAttrs,index=4)
        playerList['G'] = playerList['G'][1:]

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
            self.players[-1]['scraper'] = [TsnDotCaScraper.esByPos.prefix]

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
                if TsnDotCaScraper.esTop300.statString('team') in player:
                    print player
                    self.assertEqual(player[TsnDotCaScraper.esTop300.statString('team')], "Edmonton")
                    self.assertGreaterEqual(player[TsnDotCaScraper.esTop300.projectedPoints()], 70)
                    self.assertEqual(player[TsnDotCaScraper.esTop300.position()], 'C')
                else:
                    self.assertEqual(player[TsnDotCaScraper.esByPos.statString('team')], "Edmonton")
                    self.assertGreaterEqual(player[TsnDotCaScraper.esByPos.projectedPoints()], 70)
                    self.assertEqual(player[TsnDotCaScraper.esByPos.position()], 'C')

                McDavidFound += 1

        self.assertEquals(McDavidFound,2)

        raskFound = 0

        for player in data:
            if str(player['name']) == "Tuukka Rask":
                self.assertEqual(player[TsnDotCaScraper.esByPos.statString('team')], "Boston")
                self.assertGreaterEqual(player[TsnDotCaScraper.esByPos.projectedWins()], 35)
                self.assertGreaterEqual(player[TsnDotCaScraper.esByPos.projectedString('savePercentage')], 0.925)
                self.assertEqual(player[TsnDotCaScraper.esByPos.position()], 'G')
                raskFound += 1

        self.assertEquals(raskFound,1)

