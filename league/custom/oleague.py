'''
Created on Sep 5, 2016

@author: jdasilva
'''

import unittest

from db.footballdb import FootballPlayerDB
from league.football import FootballLeague

class OLeagueFootballLeague(FootballLeague):
    def __init__(self):
        from cli.cmd.command import SearchByPositionCommand

        name = "O-League"
        rules = None
        db = FootballPlayerDB(name)
        super(OLeagueFootballLeague, self).__init__(name, db, rules)
        self.property['isAuctionDraft'] = 'true'
        db.load()

        self.parser.commands.append(SearchByPositionCommand('all'))
        self.parser.commands.append(SearchByPositionCommand('qb'))
        self.parser.commands.append(SearchByPositionCommand('wr'))
        self.parser.commands.append(SearchByPositionCommand('te'))
        self.parser.commands.append(SearchByPositionCommand('rb'))

        self.parser.autosave = True


    def factoryReset(self):

        from sitescraper.nfl.footballdbdotcom import FootballDBDotComScraper
        from sitescraper.multisport.rotoworlddotcom import RotoWorldDotComScraper

        self.db = FootballPlayerDB(self.name)
        self.db.wget(scrapers=[FootballDBDotComScraper()])

        rotoScrape = RotoWorldDotComScraper()
        for p in self.db.player:
            if 'DEF' in self.db.player[p].position:
                continue
            print "RotoWorld: Learning about " + self.db.player[p].name + "..."
            pStats = rotoScrape.scrape(playerName=self.db.player[p].name, league="nfl")
            if pStats is not None:
                self.db.player[p].update(pStats)



class OLeagueFootballLeagueTest(unittest.TestCase):

    def testConstructor(self):

        ffl = OLeagueFootballLeague()
        self.assertNotEquals(ffl, None)
        self.assertEquals(ffl.property['isAuctionDraft'], 'true')
        self.assertEquals(ffl.name,"O-League")
        self.assertEquals(ffl.db.league,"O-League")

        pass


if __name__ == "__main__":
    unittest.main()