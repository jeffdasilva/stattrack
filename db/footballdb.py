#!/usr/bin/env python

from datetime import datetime
import os
import unittest
import pandas as pd

from db.player.football import FootballPlayer
from db.player.player import Player
from db.playerdb import PlayerDB
from league.rules import FootballRules
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

        self.positions = ['qb', 'wr', 'rb']

        self.playerCache = {}
        self.cost_per_value_unit = None
        
        self.numberOfStarting = {}
        self.numberTotalToDraft = {}
    
    
    def wget(self, scrapers=[]):
        allScrapers = scrapers + [FantasyProsDotComScraper()]

        for s in allScrapers:
            data = s.scrape()
            for player_prop in data:
                player = FootballPlayer(properties=player_prop)
                self.add(player)

    
    def update(self, playerData):
        super(FootballPlayerDB, self).update(playerData)
      
    def update_auction_stats(self):
        #self.debug = True  
        if self.debug: print ("[UPDATE Auction Stats: START]")
        
        # order matters
        self.updateMoneyRemaining()
        self.updatePlayerCache()
        self.updateValueRemaining()
        self.updateCostPerValueUnit()
        self.updatePlayerAuctionCostValues()

        if self.debug: print ("[UPDATE Auction Stats: END]")


    def updateMoneyRemaining(self):
        money_remaining = self.numberOfTeams * self.moneyPerTeam
        for p in self.player.itervalues():
            if p.isDrafted:
                money_remaining = money_remaining - p.cost
        self.money_remaining = money_remaining

    def updateRemainingPlayersByPosition(self):
        self.num_players_remaining = {}
        self.players_remaining = {}
        self.drafted_players = {}
        for position in self.positions: 
            assert(position in self.numberTotalToDraft)
            self.drafted_players[position] = self.numberOfPlayersDrafted(position=position)
            self.num_players_remaining[position] = self.numberTotalToDraft[position] - self.drafted_players[position]
            self.players_remaining[position] = self.get(position=position)[:self.num_players_remaining[position]]

    def updatePlayerCache(self):
        if self.debug: print ("[UPDATE Player Cache: START]")
        self.updateRemainingPlayersByPosition()

        self.total_num_players_remaining = int(self.totalNumberOfPlayers*self.numberOfTeams) - self.numberOfPlayersDrafted()
        self.playerCache['all'] = self.get()[:self.total_num_players_remaining]
        self.playerCache['starters'] = []
        for p in self.positions:
            self.playerCache[p] = self.players_remaining[p]
            self.playerCache['starters'].extend(self.playerCache[p])

        '''
        ####
        remainingDraftEligiblePlayers = self.playerCache['all']
        remainingDraftEligibleStarters = self.remainingStarters()

        for p in remainingDraftEligibleStarters:
            if p in remainingDraftEligiblePlayers:
                remainingDraftEligiblePlayers.remove(p)

        self.playerCache['bench'] = remainingDraftEligiblePlayers
        ####
        '''
            
        if self.debug: print ("[UPDATE Player Cache: END]")

        
    def updateValueRemaining(self):
        total_value = 0.0
        '''
        for p in self.playerCache['starters']:
            player_value = float(p.value())
            value += player_value
        '''
        
        self.value_remaining_by_position = {}
        
        for pos in self.positions:
            self.value_remaining_by_position[pos] = 0        
            for p in self.players_remaining[pos]:
                player_value = float(p.value())
                self.value_remaining_by_position[pos] += player_value
                total_value += player_value
                        
        self.value_remaining = total_value
        
    def updateMeanAbsoluteDeviation(self):
        self.playerValueMAD = {}
        self.playerValueMADTotal = 0.0
        for position in self.positions:
            players = self.players_remaining[position]
            if len(players) == 0: 
                self.playerValueMAD[position] = 0
                continue
        
            values = []
            for p in players:
                values.append(float(p.value())) 
            series = pd.Series(values)
            result = series.mad()
            self.playerValueMAD[position] = result
            self.playerValueMADTotal += result
    
    def updateCostPerValueUnit(self):
        self.updateMeanAbsoluteDeviation()
        money_remaining = float(max(self.money_remaining,1))
        value_remaining = float(max(self.value_remaining,1.0))
        self.cost_per_value_unit =  money_remaining / value_remaining
        

        self.money_remaining_by_position = {}
        unnormalized_money_remaining = 0.0
        for pos in self.positions:
            self.money_remaining_by_position[pos] = money_remaining * (self.value_remaining_by_position[pos] / value_remaining)
            
            # scale the numbers based on MAD factor
            self.money_remaining_by_position[pos] *= (self.playerValueMAD[pos] / self.playerValueMADTotal)
            unnormalized_money_remaining += self.money_remaining_by_position[pos]
            
        # normalize the numbers so that it still equals total value_remaining 
        normalizing_multiplier = money_remaining / unnormalized_money_remaining
        for pos in self.positions:
            self.money_remaining_by_position[pos] *= normalizing_multiplier
            
            
        self.cost_per_value_unit_by_position = {}
        for pos in self.positions:
            self.cost_per_value_unit_by_position[pos] = self.money_remaining_by_position[pos] /self.value_remaining_by_position[pos]


    def updatePlayerAuctionCostValues(self):
        for pos in self.positions:
            for player in self.players_remaining[pos]:
                player.auction_value = self.cost_per_value_unit_by_position[pos] * float(player.value())
            
            
            
            
            '''
                (self.playerValueMAD[pos] / self.playerValueMADTotal) * \
                3*(self.value_remaining_by_position[pos] / value_remaining)
            '''
        
        '''
        self.pointsRemainingMAD = {}
        total_mad = 0
        for pos in ['qb', 'wr', 'rb']:
            self.pointsRemainingMAD[pos] = self.meanAbsoluteDeviation(pos)
            total_mad += self.pointsRemainingMAD[pos]
        '''


    '''
    def remainingGoodPlayersByPosition(self, position):
        if position in self.numberTotalToDraft:
            num_players_total = self.numberTotalToDraft[position]
        else:
            num_players_total = int(self.numberOfStarting[position]*self.numberOfTeams)
            
        num_players_remaining = num_players_total - self.numberOfPlayersDrafted(position=position)
            
        return self.get(position=position)[:num_players_remaining]
    '''



    '''
    def remainingStarters(self):
        if 'starters' not in self.playerCache:
            self.updatePlayerCache()

        return self.playerCache['starters']

    def remainingBenchPlayers(self):
        if 'bench' not in self.playerCache:
            self.updatePlayerCache()

        return self.playerCache['bench']

    def remainingDraftEligiblePlayers(self):
        return self.remainingStarters() + self.remainingBenchPlayers()
    '''
    

    '''
    def costPerValueUnit(self, position=None):
        #if self.cost_per_value_unit is None:
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
    '''

class TestFootballPlayerDB(unittest.TestCase):
    
    def init_fdb(self, db):
        db.numberOfTeams = 10
        db.numberOfStarting = {}
        db.numberOfStarting['qb'] = 1
        db.numberOfStarting['rb'] = 5
        db.numberOfStarting['wr'] = 4
        db.numberOfScrubs = 5 
        db.totalNumberOfPlayers = 15       
        db.moneyPerTeam = 100
        FootballPlayer.DefaultRules = FootballRules()

    def testNewFootballPlayerDB(self):
        fdb = FootballPlayerDB()
        self.init_fdb(fdb)
        self.assertTrue(len(fdb.positionMap.keys()) > 5)
        self.assertEquals(fdb.positionMap["kicker"],["K"])
        pass

    def testRemainingPlayer(self):
        fdb = FootballPlayerDB()
        self.init_fdb(fdb)
        fdb.load()

        cpv_mult = fdb.costPerValueUnit()
        for p in fdb.remainingStarters():
            print str(p) + " $" + str(cpv_mult * p.value())

        print fdb.valueRemaining(), fdb.moneyRemaining(), fdb.costPerValueUnit()

    def testMoneyRemaining(self):
        fdb = FootballPlayerDB(league='O-League')
        self.init_fdb(fdb)
        self.assertEqual(fdb.moneyRemaining(),1000)
        fdb.moneyPerTeam = 333
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
        self.init_fdb(fdb)

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
        self.init_fdb(fdb)
        fdb.add(FootballPlayer("Jeff DS","SF",{"fantasyPoints":"24"}))
        fdb.add(FootballPlayer("Jeff","SF",{"fantasyPoints":"124"}))
        fdb.add(FootballPlayer("Jeffx","SF",{"fantasyPoints":"14"}))
        #self.assertEquals(fdb.get("Jeff")[0].property['fantasyPoints'],124)

    def testWgetCheatsheets(self):
        fdb = FootballPlayerDB()
        fdb.wget(scrapers=[FantasyProsDotComScraper()])
        self.init_fdb(fdb)

        p = fdb.player["julio jones - atl"]
        self.assertEquals(p.position,["WR"])

    def testSaveFile(self):
        fdb = FootballPlayerDB("O-League")
        self.assertEquals(fdb.saveFile, os.path.dirname(os.path.abspath(__file__)) + "/../data/O-League_playerdb.pickle")

    def testProjectionMethods(self):
        fdb = FootballPlayerDB()
        fdb.wget(scrapers=[FantasyProsDotComScraper()])
        self.init_fdb(fdb)
        
        for pKey in ["cam newton - car", "drew brees - no", "russell wilson - sea", "aaron rodgers - gb"]:
            p = fdb.player[pKey]
            print(p)
            print("Projected Interceptions: " + str(p.projectedPassingInterceptionsThrown()))
            print("Projected 2Pt conv: " + str(p.projectedPassingTwoPointers()))
            self.assertEqual(p.projectedPassingTwoPointers(), p.passingTwoPointers(year=2015))


if __name__ == '__main__':
    unittest.main()
