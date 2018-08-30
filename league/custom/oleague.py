'''
Created on Sep 5, 2016

@author: jdasilva
'''

import unittest

from cli.cmd.command import Command
from db.footballdb import FootballPlayerDB
from db.player.football import FootballPlayer
from league.football import FootballLeague
from league.rules import FootballRules
from sitescraper.nfl.fantasyprosdotcom import FantasyProsDotComScraper


class OLeagueFootballRules(FootballRules):

    def __init__(self):
        super(OLeagueFootballRules, self).__init__()

        # 2016
        #self.settingsURL = "https://football.fantasysports.yahoo.com/f1/66542/settings"
        # 2017
        #self.settingsURL = "https://football.fantasysports.yahoo.com/f1/159148/settings"
        # 2018
        self.settingsURL = "https://football.fantasysports.yahoo.com/f1/897722/settings"

        self.numTeams = 10
        self.moneyPerTeam = 333
        self.numQB = 2
        self.numRB = 3
        self.numWR = 4
        self.numTE = 0
        self.numDEF = 0
        numStarters = self.numQB + self.numRB + self.numWR + self.numTE + self.numDEF
        self.numReserves = 14 - numStarters

        self.pointsPerCompletion = 0.25
        self.pointsPerIncompletePass = -0.50
        self.pointsPerPassingYard = [ (0,1.0/25), (300,2.0/25), (350,4.0/25), (400,6.0/25) ]
        self.pointsPerPassingTouchdown = 6
        self.pointsPerInterception = -2
        self.pointsPerSack = -0.5
        self.pointsPerRushingAttempt = 0.1
        self.pointsPerRushingYard = [ (0,1.0/10), (100,2.0/10), (150,4.0/10), (200,6.0/10) ]
        self.pointsPerRushingTouchdown = 6
        self.pointsPerRushingTwoPointConversion = 2
        self.pointsPerReception = 1
        self.pointsPerReceivingYard = [ (0,1.0/10), (100,2.0/10), (150,4.0/10), (200,6.0/10) ]
        self.pointsPerReceivingTouchdown = 6
        self.pointsPerReceivingTwoPointConversion = 2
        self.pointsPerReturnYard = [ (0,1.0/20), (100,3.0/20), (200,6.0/20) ]
        self.pointsPerReturnTouchdown = 6
        self.pointsPerFumblesTouchdown = 6
        self.pointsPerTwoPointConversion = 2
        self.pointsPerFumble = -1
        self.pointsPerFumblesLost = -2
        self.pointsPerPickSixesThrown = -6
        self.pointsPerFortyPlusYardCompletion = 1
        self.pointsPerFortyPlusYardPassingTouchdown = 3
        self.pointsPerFortyPlusYardRun = 1
        self.pointsPerFortyPlusYardRushingTouchdown = 3
        self.pointsPerFortyPlusYardReception = 1
        self.pointsPerFortyPlusYardReceivingTouchdown = 3

        fpros_scraper = FantasyProsDotComScraper()
        fpros_scraper.setProjectionURLs(week="draft")
        self.scrapers = [ fpros_scraper ]


class OLeagueFootballLeague(FootballLeague):
    def __init__(self):
        from cli.cmd.command import SearchByPositionCommand

        name = "O-League"
        rules = OLeagueFootballRules()

        FootballPlayer.DefaultRules = rules

        db = FootballPlayerDB(name)
        super(OLeagueFootballLeague, self).__init__(name, db, rules)
        self.property['isAuctionDraft'] = 'true'
        db.load()

        self.parser.commands.append(SearchByPositionCommand('all'))
        self.parser.commands.append(SearchByPositionCommand('qb'))
        self.parser.commands.append(SearchByPositionCommand('wr'))
        self.parser.commands.append(SearchByPositionCommand('te'))
        self.parser.commands.append(SearchByPositionCommand('rb'))

        self.parser.commands.append(StatsCommand())
        # give list command some extra needed performance
        self.parser.getCommand("list").maxPlayersToList = 10

        self.parser.autosave = True

        fpros_scraper = FantasyProsDotComScraper()
        fpros_scraper.setProjectionURLs(week="draft")
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
# stats
class StatsCommand(Command):
    def __init__(self):
        super(StatsCommand, self).__init__('stats')
        self.updatesDB = False

    def help(self, args, parser):
        return "Print out the current O-League statistics"

    def apply(self, cmd, parser):
        self.statusTrue(parser)


        leagueOrResponse = self.getLeague(parser)
        if not self.isCurrentStatusTrue(parser):
            response = leagueOrResponse
            return response

        league = leagueOrResponse

        response = ""
        response += "Money Remaining: $" + str(league.db.moneyRemaining()) + "\n"
        response += "Points Remaining: " + str(round(league.db.valueRemaining(),2)) + "\n"
        response += "Cost Per Value Unit: " + str(round(league.db.costPerValueUnit(),2)) + "\n"

        return response

##########################################################


class OLeagueFootballLeagueTest(unittest.TestCase):

    def testConstructor(self):
        ffl = OLeagueFootballLeague()
        self.assertNotEquals(ffl, None)
        self.assertEquals(ffl.property['isAuctionDraft'], 'true')
        self.assertEquals(ffl.name,"O-League")
        self.assertEquals(ffl.db.leagueName,"O-League")
        self.assertNotEquals(ffl.rules,None)
        print str(ffl.rules.pointsPerPassingYard)
        pass

    def testLeagueDB(self):
        ffl = OLeagueFootballLeague()
        if len(ffl.db.player) > 0:
            #if league was previously saved, then aaron rogd
            p = ffl.db.player["aaron rodgers - gb"]
            self.assertEqual(p.passingTwoPointers(year=2015),4)
            print p
            print "Passing Attempts: " + str(p.passingAttempts())
            print "Passing TDs: " + str(p.projectedPassingTDs())


if __name__ == "__main__":
    unittest.main()