#!/usr/bin/env python

from datetime import datetime
import os
import unittest

from db.player.football import FootballPlayer
from db.player.player import Player
from db.playerdb import PlayerDB
from sitescraper.nfl.fantasyprosdotcom import FantasyProsDotComScraper

class FootballPlayerDB(PlayerDB):

    def __init__(self, league=None):

        pmap = {}
        pmap["qb"] = [ "QB" ]
        pmap["quarterback"] = [ "QB" ]
        pmap["rb"] = [ "RB" ]
        pmap["runningback"] = [ "RB" ]
        pmap["wr"] = [ "WR", "TE" ]
        pmap["widereceiver"] = [ "WR", "TE" ]
        pmap["te"] = [ "TE" ]
        pmap["tightend"] = [ "TE" ]
        pmap["k"] = [ "K" ]
        pmap["kicker"] = [ "K" ]
        pmap["def"] = [ "DEF" ]
        pmap["defence"] = [ "DEF" ]
        pmap["defense"] = [ "DEF" ]

        super(FootballPlayerDB, self).__init__(name=league, positionMap=pmap)
        self.leagueName = league

        self.playerCache = {}
        self.cost_per_value_unit = None

        if self.leagueName is None:
            self.leagueName = "Oracle"

        if self.leagueName == "O-League":
            #2016 settings
            #https://football.fantasysports.yahoo.com/f1/66542/6/settings
            self.numberOfTeams = 10
            self.numberOfStarting = {}
            self.numberOfStarting['qb'] = 2
            self.numberOfStarting['rb'] = 3
            self.numberOfStarting['wr'] = 4
            self.totalNumberOfPlayers = 14
            self.numberOfScrubs = self.totalNumberOfPlayers - self.numberOfStarting['qb'] - self.numberOfStarting['rb'] - self.numberOfStarting['wr']
            self.moneyPerTeam = 333
        elif self.leagueName == "Oracle":
            self.numberOfTeams = 16
            self.numberOfStarting = {}
            self.numberOfStarting['qb'] = 1
            self.numberOfStarting['rb'] = 3
            self.numberOfStarting['wr'] = 4
            self.numberOfScrubs = 0
            self.moneyPerTeam = 0
            self.totalNumberOfPlayers = 16
        elif self.leagueName == "IronGut":
            self.numberOfTeams = 12
            self.numberOfStarting = {}
            self.numberOfStarting['qb'] = 1
            self.numberOfStarting['rb'] = 2
            self.numberOfStarting['wr'] = 3
            self.numberOfStarting['def'] = 1
            self.numberOfStarting['k'] = 1
            self.numberOfScrubs = 0
            self.moneyPerTeam = 0
            self.totalNumberOfPlayers = 9
        else:
            raise ValueError("unknown league type")

    def wget(self, scrapers=[]):

        #allScrapers = scrapers + [FantasyProsDotComScraper()]
        allScrapers = scrapers

        for s in allScrapers:
            data = s.scrape()
            for player_prop in data:
                player = FootballPlayer(properties=player_prop)
                self.add(player)

    def moneyRemaining(self):
        total_money = self.numberOfTeams * self.moneyPerTeam

        for p in self.player.itervalues():
            if p.isDrafted:
                total_money = total_money - p.cost

        return total_money

    def remainingGoodPlayersByPosition(self, position):
        num_players_remaining = self.numberOfStarting[position]*self.numberOfTeams - self.numberOfPlayersDrafted(position=position)
        return self.get(position=position)[:num_players_remaining]

    def updatePlayerCache(self):
        if self.debug: print ("[UPDATE Player Cache: START]")

        total_num_players_remaining = self.totalNumberOfPlayers*self.numberOfTeams - self.numberOfPlayersDrafted()
        self.playerCache['all'] = self.get()[:total_num_players_remaining]
        self.playerCache['wr'] = self.remainingGoodPlayersByPosition(position="wr")
        self.playerCache['rb'] = self.remainingGoodPlayersByPosition(position="rb")
        self.playerCache['qb'] = self.remainingGoodPlayersByPosition(position="qb")
        #self.playerCache['def'] = self.remainingGoodPlayersByPosition(position="def")
        #self.playerCache['k'] = self.remainingGoodPlayersByPosition(position="k")

        self.playerCache['starters'] = self.playerCache['wr'] + self.playerCache['qb'] + self.playerCache['rb']
        # + self.playerCache['def'] + self.playerCache['k']


        ####
        remainingDraftEligiblePlayers = self.playerCache['all']
        remainingDraftEligibleStarters = self.remainingStarters()

        for p in remainingDraftEligibleStarters:
            if p in remainingDraftEligiblePlayers:
                remainingDraftEligiblePlayers.remove(p)

        self.playerCache['bench'] = remainingDraftEligiblePlayers
        ####

        self.updateCostPerValueUnit()
        if self.debug: print ("[UPDATE Player Cache: END]")


    def remainingStarters(self):
        if 'starters' not in self.playerCache:
            self.updatePlayerCache()

        return self.playerCache['starters']

    def remainingGoodBenchPlayers(self):
        if 'bench' not in self.playerCache:
            self.updatePlayerCache()

        return self.playerCache['bench']

    def remainingDraftEligiblePlayers(self):
        return self.remainingStarters() + self.remainingGoodBenchPlayers()

    def valueRemaining(self):

        if len(self.playerCache) == 0:
            self.updatePlayerCache()

        value = 0.0
        for p in self.remainingStarters():

            player_value = p.value()
            if self.leagueName == "O-League":
                if player_value < 15:
                    player_value = player_value * 0.7
                elif player_value < 10:
                    player_value = player_value * 0.4
                elif player_value < 8:
                    player_value = player_value * 0.1


            value += player_value

        # bench players are worth a lot less (0.05x compared to a starter)
        for p in self.remainingGoodBenchPlayers():

            player_value = (p.value() * 0.05)

            if self.leagueName == "O-League":
                if player_value < 10: player_value = player_value * 0.1

            value += player_value

        return value

    def updateCostPerValueUnit(self):
        self.cost_per_value_unit = self.moneyRemaining() / max(self.valueRemaining(),0.1)

    def costPerValueUnit(self, position=None):
        if self.cost_per_value_unit is None:
            self.updateCostPerValueUnit()

        mult = 1.0
        # ToDo: make this better i.e. more scientific and dynamic based on how many of each position are left
        if position is not None:
            if 'RB' in position:
                mult = mult * 1.3
            elif 'WR' in position or 'TE' in position:
                mult = mult * 1.2
            elif 'QB' in position:
                mult = mult * 0.65

        return self.cost_per_value_unit * mult


class TestFootballPlayerDB(unittest.TestCase):

    def testNewFootballPlayerDB(self):
        fdb = FootballPlayerDB()
        self.assertTrue(len(fdb.positionMap.keys()) > 5)
        self.assertEquals(fdb.positionMap["kicker"],["K"])
        pass

    def testRemainingPlayer(self):
        fdb = FootballPlayerDB()
        fdb.load()

        cpv_mult = fdb.costPerValueUnit()
        for p in fdb.remainingStarters():
            print str(p) + " $" + str(cpv_mult * p.value())

        print fdb.valueRemaining(), fdb.moneyRemaining(), fdb.costPerValueUnit()

    def testMoneyRemaining(self):
        fdb = FootballPlayerDB(league='O-League')
        fdb.add(Player("June"))
        fdb.add(Player("Sophia"))
        self.assertEqual(fdb.moneyRemaining(),3330)

        fdb.get("June")[0].draft(10)
        self.assertEqual(fdb.moneyRemaining(),3320)

        fdb.get("Sophia")[0].draft(111)
        self.assertEqual(fdb.moneyRemaining(),3209)


    def testWget(self):
        fdb = FootballPlayerDB()
        fdb.wget(scrapers=[FantasyProsDotComScraper()])

        #print fdb.player


        p = fdb.player["tom brady - ne"]
        print p

        current_month = datetime.now().month

        if current_month > 6:
            self.assertEquals(p.position,["QB"])
            self.assertTrue(float(p.property["fantasyPoints"]) > 200)
            self.assertTrue(float(p.property["passingAttempts"]) > 300)
            self.assertTrue(p.passingYards() > 3000)
            print p.value()

        pass

    def testValAndSort(self):
        fdb = FootballPlayerDB()
        fdb.add(FootballPlayer("Jeff DS","SF",{"fantasyPoints":"24"}))
        fdb.add(FootballPlayer("Jeff","SF",{"fantasyPoints":"124"}))
        fdb.add(FootballPlayer("Jeffx","SF",{"fantasyPoints":"14"}))
        #self.assertEquals(fdb.get("Jeff")[0].property['fantasyPoints'],124)

    def testWgetCheatsheets(self):
        fdb = FootballPlayerDB()
        fdb.wget(scrapers=[FantasyProsDotComScraper()])

        p = fdb.player["julio jones - atl"]
        print p
        self.assertEquals(p.position,["WR"])

    def testSaveFile(self):
        fdb = FootballPlayerDB("O-League")
        self.assertEquals(fdb.saveFile, os.path.dirname(os.path.abspath(__file__)) + "/../data/O-League_playerdb.pickle")

    def testProjectionMethods(self):
        fdb = FootballPlayerDB()
        fdb.wget(scrapers=[FantasyProsDotComScraper()])

        for pKey in ["cam newton - car", "drew brees - no", "russell wilson - sea", "aaron rodgers - gb"]:
            p = fdb.player[pKey]
            print p
            print "Projected Interceptions: " + str(p.projectedPassingInterceptionsThrown())
            print "Projected 2Pt conv: " + str(p.projectedPassingTwoPointers())
            self.assertEqual(p.projectedPassingTwoPointers(), p.passingTwoPointers(year=2015))


if __name__ == '__main__':
    unittest.main()
