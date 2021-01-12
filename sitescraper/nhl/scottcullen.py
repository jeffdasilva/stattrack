#!/usr/bin/env python

import datetime
import unittest

from db.player.strings import HockeyPlayerStrings
from sitescraper.scraper import SiteScraper


class ScottCullenScraper(SiteScraper):

    TEAM_NAME_REAMAP = {
    'arz':'ari',
    'cbj':'clb',
    'mtl':'mon',
    'vgk':'lv',
    'wsh':'was',
    }


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
        elif str(year) in [ "2020", "2021" ]:
            # This year is special because 2020-2021 seasons starts in 2021
            offset = "/2PACX-1vTF1VL50HZ6WIMlRWqm5Ls7b0Zy-U0pwl0byW50hVxJ--UBahp8cWnJNQDge3H4X3KGoy2hau0YKVIt/pubhtml#"
        else:
            raise ValueError("projections for " + str(year) + " are not available yet")

        #tableAttrs={'class':'stats-table-scrollable article-table'}
        #data = self.scrapeTable(urlOffset=offset,attrs=tableAttrs,index=1)
        data = self.scrapeTables(urlOffset=offset)

        self.players = []

        for table in data:
            if len(table) < 2:
                continue

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
                                
                if 'position' not in player and position is not None:
                    player['position'] = position
                player['scraper'] = [ScottCullenScraper.ES.prefix]

                #print(player['name'])
                #print(", " + player['position'])

                if player[ScottCullenScraper.ES.team()] == '':
                    player[ScottCullenScraper.ES.team()] = '???'
                    
                if player[ScottCullenScraper.ES.team()].lower() in ScottCullenScraper.TEAM_NAME_REAMAP:
                    player[ScottCullenScraper.ES.team()] = ScottCullenScraper.TEAM_NAME_REAMAP[player[ScottCullenScraper.ES.team()].lower()]

                self.players.append(player)
                #print(player)
                
            break

        return self.players


class TestScottCullenScraper(unittest.TestCase):

    def testScottCullenScraper(self):
        s = ScottCullenScraper()
        s.testmode = True
        s.debug = True
        #data = s.scrape(year="2019")
        _data = s.scrape(year="2021")
        #print(str(data))


if __name__ == "__main__":
    unittest.main()