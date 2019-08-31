#!/usr/bin/env python


import unittest

from cli.cmd.command import Command
from db.footballdb import FootballPlayerDB
from db.player.football import FootballPlayer
from league.football import FootballLeague
from league.rules import FootballRules
from sitescraper.nfl.fantasyprosdotcom import FantasyProsDotComScraper


class FFLFootballRules(FootballRules):

    def __init__(self):
        super(FFLFootballRules, self).__init__()

        # 2019        
        self.settingsURL = "https://fantasy.espn.com/football/league/settings?leagueId=6549253&seasonId=2019"
        
        self.numTeams = 14
        self.moneyPerTeam = 0
        self.numQB = 1
        self.numRB = 2.5
        self.numWR = 2.5
        self.numTE = 1
        self.numDEF = 1
        self.numPK = 1
        numStarters = self.numQB + self.numRB + self.numWR + self.numTE + self.numDEF + self.numPK
        self.numReserves = 14 - numStarters  # 5

        self.pointsPerCompletion = 0.05
        self.pointsPerIncompletePass = 0
        self.pointsPerPassingYard = 0.05
        self.pointsPerPassingTouchdown = 5.0
        self.pointsPerInterception = -2.0
        self.pointsPerSack = -1.0
        self.pointsPerRushingAttempt = 0.05
        self.pointsPerRushingYard = 0.1
        self.pointsPerRushingTouchdown = 6
        self.pointsPerRushingTwoPointConversion = 3
        self.pointsPerReception = 1
        self.pointsPerReceivingYard = 0.12
        self.pointsPerReceivingTouchdown = 6
        self.pointsPerReceivingTwoPointConversion = 2.5
        self.pointsPerReturnYard = 0.1
        self.pointsPerReturnTouchdown = 7
        self.pointsPerFumblesTouchdown = 6
        self.pointsPerTwoPointConversion = 2
        self.pointsPerFumble = 0
        self.pointsPerFumblesLost = 0
        self.pointsPerPickSixesThrown = 0
        self.pointsPerFortyPlusYardCompletion = 1.5
        self.pointsPerFortyPlusYardPassingTouchdown = 2
        self.pointsPerFortyPlusYardRun = 0
        self.pointsPerFortyPlusYardRushingTouchdown = 1.5
        self.pointsPerFortyPlusYardReception = 0
        self.pointsPerFortyPlusYardReceivingTouchdown = 2

        fpros_scraper = FantasyProsDotComScraper()
        fpros_scraper.setProjectionURLs(week="draft")
        self.scrapers = [ fpros_scraper ]


class FFLFootballLeague(FootballLeague):
    
    def initdb(self, db):
        assert(self.rules is not None)
        rules = self.rules
        db.numberOfTeams = rules.numTeams
        db.numberOfStarting['qb'] = rules.numQB
        db.numberOfStarting['rb'] = rules.numRB
        db.numberOfStarting['wr'] = rules.numWR
        db.numberOfStarting['te'] = rules.numTE
        db.numberOfStarting['def'] = rules.numDEF
        db.numberOfStarting['pk'] = rules.numPK
        db.numberOfScrubs = rules.numReserves 
        db.totalNumberOfPlayers = rules.numQB + rules.numRB + rules.numWR + rules.numReserves        
        db.moneyPerTeam = rules.moneyPerTeam
    
        db.numberTotalToDraft['qb'] = rules.numQB + 1
        db.numberTotalToDraft['rb'] = rules.numRB + 1    
        db.numberTotalToDraft['wr'] = rules.numWR + 1.5
        db.numberTotalToDraft['te'] = rules.numTE + 0.5
        db.numberTotalToDraft['def'] = rules.numDEF + 0.5
        db.numberTotalToDraft['pk'] = rules.numPK + 0.5

        db.numberTotalToDraft['all'] = 0
        for pos in db.numberTotalToDraft:
            if pos == 'all': continue
            db.numberTotalToDraft['all'] += db.numberTotalToDraft[pos]
    
        assert(int(db.totalNumberOfPlayers*db.numberOfTeams) == int(db.numberTotalToDraft['all']))
    
    def __init__(self):
        from cli.cmd.command import SearchByPositionCommand

        name = "FFL"

        db = FootballPlayerDB(name)
        self.positions = ['qb', 'wr', 'rb', 'te', 'def', 'pk']
        
        rules = FFLFootballRules()
        FootballPlayer.DefaultRules = rules

        super(FFLFootballLeague, self).__init__(name, db, rules)
        self.initdb(db)
        db.load()
             
        self.parser.commands.append(SearchByPositionCommand('all'))
        for p in db.positions:
            self.parser.commands.append(SearchByPositionCommand(p))

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


class FFLFootballLeagueTest(unittest.TestCase):

    def testConstructor(self):
        ffl = FFLFootballLeague()
        self.assertNotEquals(ffl, None)
        self.assertEquals(ffl.name,"FFL")
        self.assertEquals(ffl.db.leagueName,"FFL")
        self.assertNotEquals(ffl.rules,None)
        print str(ffl.rules.pointsPerPassingYard)

if __name__ == "__main__":
    unittest.main()