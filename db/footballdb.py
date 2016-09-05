'''
Created on April 12, 2016

@author: jdasilva
'''

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


        super(FootballPlayerDB, self).__init__(positionMap=pmap,name=league)
        self.league = league

        if self.league is None:
            self.league = "Oracle"

        if self.league == "O-League":
            #2016 settings
            #https://football.fantasysports.yahoo.com/f1/66542/6/settings
            self.numberOfTeams = 10
            self.numberOfStarting = {}
            self.numberOfStarting['qb'] = 2
            self.numberOfStarting['rb'] = 3
            self.numberOfStarting['wr'] = 4
            self.numberOfScrubs = 14 - self.numberOfStarting['qb'] - self.numberOfStarting['rb'] - self.numberOfStarting['wr']
            self.moneyPerTeam = 333
        elif self.league == "Oracle":
            self.numberOfTeams = 16
            self.numberOfStarting = {}
            self.numberOfStarting['qb'] = 1
            self.numberOfStarting['rb'] = 3
            self.numberOfStarting['wr'] = 4
            self.numberOfScrubs = 0
            self.moneyPerTeam = 0
        else:
            raise ValueError("unknown league type")

    def wget(self, scrapers=[]):

        allScrapers = scrapers + [FantasyProsDotComScraper()]

        for s in allScrapers:
            s.scrape()
            for player_prop in s.data:
                player = FootballPlayer(properties=player_prop)
                self.add(player)

    def moneyRemaining(self):
        total_money = self.numberOfTeams * self.moneyPerTeam

        for p in self.player.itervalues():
            if p.isDrafted:
                total_money -= p.cost

        return total_money

    def remainingGoodPlayersByPosition(self, position):
        num_players_remaining = self.numberOfStarting[position]*self.numberOfTeams - self.numberOfPlayersDrafted(position=position)
        return self.get(position=position)[:num_players_remaining]

    def remainingGoodPlayers(self):
        return max(self.remainingGoodPlayersByPosition(position="wr"),3) \
            + max(self.remainingGoodPlayersByPosition(position="qb"),3) \
            + max(self.remainingGoodPlayersByPosition(position="rb"),3)

    def valueRemaining(self):
        value = 0
        for p in self.remainingGoodPlayers():
            value += p.value()
        return value

    def costPerValueUnit(self):
        return self.moneyRemaining() / max(self.valueRemaining(),0.1)


class TestFootballPlayer(unittest.TestCase):

    def testNewFootballPlayer(self):
        fp = FootballPlayer(name="Jeff", team="SF", properties={"position":"WR","foo":"bar","name":"DaSilva"})

        self.assertEquals(fp.name,"DaSilva")
        self.assertEquals(fp.team,"SF")
        self.assertEquals(fp.position,["WR"])
        self.assertEquals(fp.property["foo"],"bar")


class TestFootballPlayerDB(unittest.TestCase):

    def testNewFootballPlayerDB(self):
        fdb = FootballPlayerDB()
        self.assertTrue(len(fdb.positionMap.keys()) > 5)
        #self.assertEquals(fdb.positionMap["kicker"],["K"])
        pass

    def testRemainingPlayer(self):
        fdb = FootballPlayerDB()
        fdb.load()

        cpv_mult = fdb.costPerValueUnit()

        for p in fdb.remainingGoodPlayers():
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
        fdb.wget()

        #print fdb.player

        p = fdb.player["tom brady - ne"]
        print p
        #self.assertEquals(p.position,["QB"])
        #self.assertTrue(float(p.property["fantasyPoints"]) > 200)
        #self.assertTrue(float(p.property["passingAttempts"]) > 500)
        #self.assertTrue(float(p.property["passingYards"]) > 3000)

        print p.value()

        p = fdb.player["rob gronkowski - ne"]
        self.assertEquals(p.position,["TE"])
        #self.assertTrue(p.property["fantasyPoints"] > 100)
        #self.assertTrue(p.property["receivingYards"] > 400)

        #p = fdb.player["Garrett Hartley - PIT"]
        #self.assertEquals(p.position,["K"])
        #self.assertTrue(p.property["fantasyPoints"] > 100)
        #self.assertTrue(p.property["extraPoints"] > 10)

        #p = fdb.player["Calvin Johnson - unknown"]
        #self.assertEquals(p.position,["WR"])
        #self.assertTrue(p.property["fantasyPoints"] > 180)
        #self.assertTrue(p.property["receivingYards"] > 400)

        pass

    def testValAndSort(self):
        fdb = FootballPlayerDB()
        fdb.add(FootballPlayer("Jeff DS","SF",{"fantasyPoints":"24"}))
        fdb.add(FootballPlayer("Jeff","SF",{"fantasyPoints":"124"}))
        fdb.add(FootballPlayer("Jeffx","SF",{"fantasyPoints":"14"}))
        #self.assertEquals(fdb.get("Jeff")[0].property['fantasyPoints'],124)

    def testWgetCheatsheets(self):
        fdb = FootballPlayerDB()
        fdb.wget()

        p = fdb.player["julio jones - atl"]
        print p
        self.assertEquals(p.position,["WR"])

    def testSaveFile(self):
        fdb = FootballPlayerDB("O-League")

        self.assertEquals(fdb.saveFile, os.path.dirname(os.path.abspath(__file__)) + "/../data/playerdb.pickle")

if __name__ == '__main__':
    unittest.main()
