#!/usr/bin/env python


import unittest

from db.footballdb import FootballPlayerDB
from db.player.football import FootballPlayer
from league.football import FootballLeague
from league.rules import FootballRules
from sitescraper.nfl.fantasyprosdotcom import FantasyProsDotComScraper


class FFLFootballRules(FootballRules):

    def __init__(self):
        super(FFLFootballRules, self).__init__()

        # 2019
        # self.settingsURL = "https://fantasy.espn.com/football/league/settings?leagueId=6549253&seasonId=2019"
        # 2020
        self.settingsURL = "https://fantasy.espn.com/football/league/settings?leagueId=6549253&seasonId=2020"

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
        # 3 IR in 2020 (2 reserved for covid)

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
        db.numberOfStarting['k'] = rules.numPK
        db.numberOfScrubs = rules.numReserves
        db.totalNumberOfPlayers = rules.numQB + rules.numRB + rules.numWR + rules.numReserves
        db.moneyPerTeam = rules.moneyPerTeam

        db.numberTotalToDraft['qb'] = rules.numQB + 1
        db.numberTotalToDraft['rb'] = rules.numRB + 1
        db.numberTotalToDraft['wr'] = rules.numWR + 1.5
        db.numberTotalToDraft['te'] = rules.numTE + 0.5
        db.numberTotalToDraft['def'] = rules.numDEF + 0.5
        db.numberTotalToDraft['k'] = rules.numPK + 0.5

        db.numberTotalToDraft['all'] = 0
        for pos in db.numberTotalToDraft:
            if pos == 'all': continue
            db.numberTotalToDraft['all'] += db.numberTotalToDraft[pos]

        #assert(int(db.totalNumberOfPlayers*db.numberOfTeams) == int(db.numberTotalToDraft['all']))

    def __init__(self):
        from cli.cmd.command import SearchByPositionCommand

        name = "FFL"

        db = FootballPlayerDB(name)
        db.positions = ['qb', 'wr', 'rb', 'te', 'def', 'k']

        rules = FFLFootballRules()
        FootballPlayer.DefaultRules = rules

        super(FFLFootballLeague, self).__init__(name, db, rules)
        self.initdb(db)
        db.load()

        self.parser.commands.append(SearchByPositionCommand('all'))
        for p in db.positions:
            self.parser.commands.append(SearchByPositionCommand(p))

        #some extra needed performance???
        #self.parser.getCommand("list").maxPlayersToList = 10

        self.parser.autosave = True

        fpros_scraper = FantasyProsDotComScraper()
        fpros_scraper.setProjectionURLs(week="draft")
        self.scrapers = [ fpros_scraper ]


    def factoryReset(self):
        #from sitescraper.nfl.footballdbdotcom import FootballDBDotComScraper
        self.db = FootballPlayerDB(self.name)
        self.initdb(self.db)

        # does this have any value?
        # self.db.wget(scrapers=[FootballDBDotComScraper()])
        # removed because it messes everything up and I don't want to debug it

    def update(self):
        self.db.wget(self.scrapers)


class FFLFootballLeagueTest(unittest.TestCase):

    def testConstructor(self):
        ffl = FFLFootballLeague()
        self.assertNotEquals(ffl, None)
        self.assertEquals(ffl.name,"FFL")
        self.assertEquals(ffl.db.leagueName,"FFL")
        self.assertNotEquals(ffl.rules,None)
        print(str(ffl.rules.pointsPerPassingYard))

if __name__ == "__main__":
    unittest.main()