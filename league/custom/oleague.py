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
        # self.settingsURL = "https://football.fantasysports.yahoo.com/f1/897722/settings"
        # 2019        
        self.settingsURL = "https://football.fantasysports.yahoo.com/f1/410075/5/settings"
        
        self.numTeams = 10
        self.moneyPerTeam = 333
        self.numQB = 2
        self.numRB = 2.5 # 3 #2.5
        self.numWR = 3.5   # 4 #3
        self.numTE = 0 # 0.5 # 0 #0.5
        self.numDEF = 0
        numStarters = self.numQB + self.numRB + self.numWR + self.numTE + self.numDEF
        self.numReserves = 13 - numStarters  # 5

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
    
    def initdb(self, db):
        assert(self.rules is not None)
        rules = self.rules
        db.numberOfTeams = rules.numTeams
        db.numberOfStarting['qb'] = rules.numQB
        db.numberOfStarting['rb'] = rules.numRB
        db.numberOfStarting['wr'] = rules.numWR
        db.numberOfStarting['te'] = rules.numTE
        db.numberOfScrubs = rules.numReserves 
        db.totalNumberOfPlayers = rules.numQB + rules.numRB + rules.numWR + rules.numReserves        
        db.moneyPerTeam = rules.moneyPerTeam
    
        # 0.8, 1.6, and 2.6 are my best guess
        #  would be good to make those numbers accurate somehow for the future
        db.numberTotalToDraft['qb'] = int((rules.numQB+0.9)*rules.numTeams)
        db.numberTotalToDraft['rb'] = int((rules.numRB+1.5)*rules.numTeams)    
        db.numberTotalToDraft['wr'] = int((rules.numWR+2.6)*rules.numTeams) 
        db.numberTotalToDraft['all'] = 0
        
        for k in db.numberTotalToDraft:
            if 'k' == 'all': continue
            db.numberTotalToDraft['all'] += db.numberTotalToDraft[k]
    
        assert(int(db.totalNumberOfPlayers*db.numberOfTeams) == int(db.numberTotalToDraft['all']))
    
    def __init__(self):
        from cli.cmd.command import SearchByPositionCommand

        name = "O-League"

        db = FootballPlayerDB(name)
        
        rules = OLeagueFootballRules()
        FootballPlayer.DefaultRules = rules

        super(OLeagueFootballLeague, self).__init__(name, db, rules)
        self.initdb(db)
        db.load()

        self.property['isAuctionDraft'] = 'true'

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
        #from sitescraper.nfl.footballdbdotcom import FootballDBDotComScraper
        self.db = FootballPlayerDB(self.name)
        self.initdb(self.db)        
        
        # does this have any value?
        #self.db.wget(scrapers=[FootballDBDotComScraper()])

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
        assert(cmd is not None)
        self.statusTrue(parser)

        leagueOrResponse = self.getLeague(parser)
        if not self.isCurrentStatusTrue(parser):
            response = leagueOrResponse
            return response

        league = leagueOrResponse
        
        league.db.update_auction_stats()
        
        response = ""
        response += "Total Money Remaining: $" + str(league.db.money_remaining) + "\n"
        
        response += "Total Points Remaining: " + str(round(league.db.value_remaining,2)) + "\n"
        response += "AVG Cost Per Value Unit: " + str(round(league.db.cost_per_value_unit,2)) + "\n"
        
        for pos in ['qb', 'wr', 'rb']:
            response += "Remaining " + pos + "'s: " + str(len(league.db.players_remaining[pos]))  + "\n"
            response += "MAD " + pos + ": " + str(round(league.db.playerValueMAD[pos],2)) + "\n"
            response += "Money Remaining " + pos + ": $" + str(round(league.db.money_remaining_by_position[pos],2)) + "\n"
            response += "Cost Per Value Unit " + pos + ": $" + str(round(league.db.cost_per_value_unit_by_position[pos],2)) + "\n"

        
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
            #self.assertEqual(p.passingTwoPointers(year=2015),4)
            print p
            print "Passing Attempts: " + str(p.passingAttempts())
            print "Passing TDs: " + str(p.projectedPassingTDs())


if __name__ == "__main__":
    unittest.main()