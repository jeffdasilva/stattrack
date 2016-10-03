'''
Created on Sep 5, 2016

@author: jdasilva
'''

import unittest

from cli.cmd.command import Command
from db.footballdb import FootballPlayerDB
from league.football import FootballLeague
from league.rules import FootballRules


class OLeagueFootballRules(FootballRules):

    def __init__(self):
        super(FootballRules, self).__init__()

        self.settingsURL = "https://football.fantasysports.yahoo.com/f1/66542/settings"

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
        self.pointsPerPassingYards = [ (0,1.0/25), (300,2.0/25), (350,4.0/25), (400,6.0/25) ]
        self.pointsPerPassingTouchdown = 6
        self.pointsPerInterception = -2
        self.pointsPerSack = -0.5
        self.pointsPerRushingAttempt = 0.1
        self.pointsPerRushingYard = [ (0,1.0/10), (100,2.0/10), (150,4.0/10), (200,6.0/10) ]
        self.pointsPerRushingTouchdown = 6
        self.pointsPerReception = 1
        self.pointsPerReceivingYard = [ (0,1.0/10), (100,2.0/10), (150,4.0/10), (200,6.0/10) ]
        self.pointsPerReceivingTouchdown = 6
        self.pointsPerReturnYard = [ (0,1.0/20), (100,3.0/20), (200,6.0/20) ]
        self.pointsPerReturnTouchdown = 6
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


class OLeagueFootballLeague(FootballLeague):
    def __init__(self):
        from cli.cmd.command import SearchByPositionCommand

        name = "O-League"
        rules = OLeagueFootballRules()
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

        self.parser.autosave = True


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
        print str(ffl.rules.pointsPerPassingYards)
        pass

    def testLeagueDB(self):
        ffl = OLeagueFootballLeague()

        p = ffl.db.player["aaron rodgers - gb"]
        self.assertEqual(p.passingTwoPointers(year=2015),4)
        print p
        print "Passing Attempts: " + str(p.passingAttempts())
        print "Passing TDs: " + str(p.projectedPassingTDs())


if __name__ == "__main__":
    unittest.main()