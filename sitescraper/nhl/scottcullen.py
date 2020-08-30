#!/usr/bin/env python

import datetime
import unittest

from db.player.strings import HockeyPlayerStrings
from sitescraper.scraper import SiteScraper


class ScottCullenScraper(SiteScraper):

    ES = HockeyPlayerStrings('scottcullen')

    ProjectedGamesPlayed = [ES.projectedGamesPlayed()]
    ProjectedGoals = [ES.projectedGoals()]
    ProjectedAssists = [ES.projectedAssists()]
    #ProjectedWins = [ES.projectedWins()]
    #ProjectedTies = [ES.projectedTies()]
    #ProjectedShutouts = [ES.projectedShutouts()]

    def __init__(self):
        super(ScottCullenScraper, self).__init__(url="https://docs.google.com/spreadsheets/d/e")

        self.maxCacheTime = datetime.timedelta(days=1)

        self.stat_map = {
            'player': ScottCullenScraper.ES.name(),
            'team': ScottCullenScraper.ES.team(),
            'g': ScottCullenScraper.ES.projectedGoals(),
            'a': ScottCullenScraper.ES.projectedAssists(),
            'pts': ScottCullenScraper.ES.projectedPoints(),
            'gp': ScottCullenScraper.ES.projectedGamesPlayed(),
            'pos':  ScottCullenScraper.ES.position(),
            }


    def scrape(self, year=datetime.datetime.now().year):

        # scrape Scott Cullen's projections
        if str(year) == "2019":
            #offset = "/2PACX-1vS67DjgNW1vzTR3CSpRuARm1xJKHQXyseaXCgKtbCdCVsCQadIOg84ZVNCziy3I28ctaeMVn5nZ5Etx/pubhtml#"
            offset = "/2PACX-1vS67DjgNW1vzTR3CSpRuARm1xJKHQXyseaXCgKtbCdCVsCQadIOg84ZVNCziy3I28ctaeMVn5nZ5Etx/pubhtml#"
        else:
            raise ValueError("projections for " + str(year) + " are not available yet")

        #tableAttrs={'class':'stats-table-scrollable article-table'}
        #data = self.scrapeTable(urlOffset=offset,attrs=tableAttrs,index=1)
        data = self.scrapeTables(urlOffset=offset)

        self.players = []

        for table in data:
            if len(table) < 2: continue

            ptable = table
            if len(ptable[0]) == 0:
                ptable = ptable[1:]

            assert(len(ptable[0]) > 0)

            assert(len(ptable[0][0]) > 0)

            if (len(ptable[0][1]) == 0):
                position = ptable[0][0]
                ptable = ptable[1:]
            else:
                position = None

            stats = []
            for col in ptable[0]:
                col = col.lower()
                statname = self.stat_map.get(col, ScottCullenScraper.ES.statString(col))
                stats.append(statname)

            ptable = ptable[1:]

            for row in ptable:
                player = dict(zip(stats,row))
                if player['name'] == '': continue
                #print(str(player))
                if 'position' not in player and position is not None:
                    player['position'] = position
                player['scraper'] = [ScottCullenScraper.ES.prefix]

                if player[ScottCullenScraper.ES.team()] == '':
                    print(str(player))
                    assert(False)

                self.players.append(player)

            break

        return self.players


class TestScottCullenScraper(unittest.TestCase):

    def testScottCullenScraper(self):
        s = ScottCullenScraper()
        s.testmode = True
        s.debug = True
        data = s.scrape(year="2019")
        print(str(data))


if __name__ == "__main__":
    unittest.main()