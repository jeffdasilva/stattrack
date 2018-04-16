'''
Created on Sep 5, 2016

@author: jdasilva
'''

import unittest

from db.footballdb import FootballPlayerDB
from league.football import FootballLeague
from league.rules import FootballRules


class IronGutFootballRules(FootballRules):

    def __init__(self):
        super(FootballRules, self).__init__()

        self.settingsURL = "http://www57.myfantasyleague.com/2016/options?L=62153&O=09"
        self.settingsURL = "http://www57.myfantasyleague.com/2017/options?L=71847&O=09"


        self.numTeams = 12
        self.numQB = 1
        self.numRB = 2
        self.numWR = 3
        self.numTE = 1
        self.numDEF = 1
        self.numK = 1
        self.numReserves = 0

        #################################################
        # Passing
        self.pointsPerCompletion = 0.0
        self.pointsPerIncompletePass = 0.0
        self.pointsPerPassingYard = 1.0/25
        self.pointsPerPassingTouchdown = 4
        self.pointsPerInterception = -1
        self.pointsPerSack = 0
        self.pointsPerPassingTwoPointConversion = 1

        # Rushing
        self.pointsPerRushingAttempt = 0
        self.pointsPerRushingYard = 1.0/10
        self.pointsPerRushingTouchdown = 6
        self.pointsPerRushingTwoPointConversion = 2

        # Receiving
        self.pointsPerReception = 0.5
        self.pointsPerReceivingYard = 1.0/10
        self.pointsPerReceivingTouchdown = 6
        self.pointsPerReceivingTwoPointConversion = 1

        # Special Teams
        self.pointsPerReturnYard = 0
        self.pointsPerReturnTouchdown = 0
        self.pointsPerTwoPointConversion = 1
        self.pointsPerFumble = 0
        self.pointsPerFumblesLost = 0

        # Other
        self.pointsPerPickSixesThrown = -4
        self.pointsPerFortyPlusYardCompletion = 0
        self.pointsPerFortyPlusYardPassingTouchdown = 0
        self.pointsPerFortyPlusYardRun = 0
        self.pointsPerFortyPlusYardRushingTouchdown = 0
        self.pointsPerFortyPlusYardReception = 0
        self.pointsPerFortyPlusYardReceivingTouchdowns = 0
        #################################################

class IronGutFootballLeague(FootballLeague):
    def __init__(self):
        from cli.cmd.command import SearchByPositionCommand
        from sitescraper.nfl.fantasyprosdotcom import FantasyProsDotComScraper

        name = "IronGut"
        rules = IronGutFootballRules()
        db = FootballPlayerDB(name)
        super(IronGutFootballLeague, self).__init__(name, db, rules)
        db.load()

        self.parser.commands.append(SearchByPositionCommand('all'))
        self.parser.commands.append(SearchByPositionCommand('qb'))
        self.parser.commands.append(SearchByPositionCommand('wr'))
        self.parser.commands.append(SearchByPositionCommand('te'))
        self.parser.commands.append(SearchByPositionCommand('rb'))
        self.parser.commands.append(SearchByPositionCommand('def'))
        self.parser.commands.append(SearchByPositionCommand('k'))

        fpros_scraper = FantasyProsDotComScraper()
        fpros_scraper.setProjectionURLs(week="18")
        self.scrapers = [ fpros_scraper ]


    def factoryReset(self):

        from sitescraper.nfl.footballdbdotcom import FootballDBDotComScraper
        from sitescraper.multisport.rotoworlddotcom import RotoWorldDotComScraper

        self.db = FootballPlayerDB(self.name)
        self.db.wget(scrapers=[FootballDBDotComScraper()])

        rotoScrape = RotoWorldDotComScraper(league="nfl")
        for p in self.db.player:
            if 'DEF' in self.db.player[p].position:
                continue
            #print "RotoWorld: Learning about " + self.db.player[p].name + "..."
            pStats = rotoScrape.scrape(playerName=self.db.player[p].name)
            if pStats is not None:
                self.db.player[p].update(pStats)


    def update(self):
        self.db.wget(self.scrapers)



##########################################################


class IronGutFootballLeagueTest(unittest.TestCase):

    def testConstructor(self):
        ffl = IronGutFootballLeague()
        self.assertNotEquals(ffl, None)
        self.assertEquals(ffl.property['isAuctionDraft'], 'false')
        self.assertEquals(ffl.name,"IronGut")
        self.assertEquals(ffl.db.leagueName,"IronGut")
        self.assertNotEquals(ffl.rules,None)
        print(str(ffl.rules.pointsPerPassingYard))
        pass

    def testLeagueDB(self):
        ffl = IronGutFootballLeague()
        if len(ffl.db.player) > 0:
            #if league was previously saved, then aaron rogd
            p = ffl.db.player["aaron rodgers - gb"]
            self.assertGreaterEqual(p.passingTwoPointers(year=2015),4)
            print(p)
            print("Passing Attempts: " + str(p.passingAttempts()))
            print("Passing TDs: " + str(p.projectedPassingTDs()))


if __name__ == "__main__":
    unittest.main()