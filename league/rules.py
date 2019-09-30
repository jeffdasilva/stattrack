#!/usr/bin/env python

import datetime
import unittest


class Rules(object):
    def __init__(self):
        pass

class HockeyRules(Rules):

    def __init__(self):
        super(HockeyRules, self).__init__()

        self.numTeams = 16
        self.numForwards = 8
        self.numDefensmen = 5
        self.numGoalies = 2
        self.numReserves = 4

        self.pointsPerGoal = 1
        self.pointsPerAssist = 1
        self.pointsPerGoalieWin = 2
        self.pointsPerGoalieShutout = 2


class FootballRules(Rules):

    def __init__(self):
        super(FootballRules, self).__init__()

        self.numTeams = 10
        self.numQB = 2
        self.numRB = 3
        self.numWR = 4
        self.numTE = 0
        self.numDEF = 0
        self.numPK = 0
        numStarters = self.numQB + self.numRB + self.numWR + self.numTE + self.numDEF + self.numPK
        self.numReserves = 13 - numStarters

        #################################################
        # Passing
        self.pointsPerCompletion = 0.0
        self.pointsPerIncompletePass = 0.0
        self.pointsPerPassingYard = [ (0,1.0/25), (300,2.0/25), (350,4.0/25), (400,6.0/25) ]
        self.pointsPerPassingTouchdown = 4
        self.pointsPerInterception = -1
        self.pointsPerSack = 0
        self.pointsPerPassingTwoPointConversion = 0

        # Rushing
        self.pointsPerRushingAttempt = 0
        self.pointsPerRushingYard = [ (0,0.1), (100,0.2), (150,0.4), (200,0.6) ]
        self.pointsPerRushingTouchdown = 6
        self.pointsPerRushingTwoPointConversion = 2

        # Receiving
        self.pointsPerReception = 1
        self.pointsPerReceivingYard = [ (0,0.1), (100,0.2), (150,0.4), (200,0.6) ]
        self.pointsPerReceivingTouchdown = 6
        self.pointsPerReceivingTwoPointConversion = 2

        # Special Teams
        self.pointsPerReturnYard = [ (0,1.0/20), (100,3.0/20), (200,6.0/20) ]
        self.pointsPerReturnTouchdown = 6
        self.pointsPerTwoPointConversion = 2
        self.pointsPerFumble = 0
        self.pointsPerFumblesLost = -2
        self.pointsPerFumblesTouchdown = 6

        # Other
        self.pointsPerPickSixesThrown = 0
        self.pointsPerFortyPlusYardCompletion = 0
        self.pointsPerFortyPlusYardPassingTouchdown = 0
        self.pointsPerFortyPlusYardRun = 0
        self.pointsPerFortyPlusYardRushingTouchdown = 0
        self.pointsPerFortyPlusYardReception = 0
        self.pointsPerFortyPlusYardReceivingTouchdowns = 0
        #################################################

    def get_scaled_multiplier(self, avg, scaledlist):
        assert(isinstance(scaledlist,list))
        mult_weight = 1
        mult = scaledlist[0][1]
        for i in scaledlist:
            if avg > (i[0]/2):
                mult = (mult*mult_weight + i[1]) / (mult_weight+1)
                mult_weight = mult_weight + 5
        return mult

    def yardPoints(self, player, yard_stat, year, points_per_yard):
        gamesPlayed = player.gamesPlayed(year)
        if gamesPlayed == 0: return 0.0
        points = 0.0
        avgYardsPerGame = yard_stat / player.gamesPlayed(year)

        if not isinstance(points_per_yard,(list,tuple)):
            mult = points_per_yard
        else:
            mult = self.get_scaled_multiplier(avgYardsPerGame, points_per_yard)

        points += (mult * avgYardsPerGame) * gamesPlayed

        return points

    def passingYardPoints(self, player, year=datetime.datetime.now().year):
        return self.yardPoints(player,player.passingYards(year),year,self.pointsPerPassingYard)

    def rushingYardPoints(self, player, year=datetime.datetime.now().year):
        return self.yardPoints(player,player.rushingYards(year),year,self.pointsPerRushingYard)

    def receivingYardPoints(self, player, year=datetime.datetime.now().year):
        return self.yardPoints(player,player.receivingYards(year),year,self.pointsPerReceivingYard)

    def passingPoints(self, player, year=datetime.datetime.now().year):
        points = 0.0
        points += self.passingYardPoints(player=player,year=year)
        points += player.passingTDs(year) * (self.pointsPerPassingTouchdown)
        points += player.passingInterceptionsThrown(year) * (self.pointsPerInterception)
        points += player.passingTwoPointers(year) * (self.pointsPerTwoPointConversion)
        return points

    def rushingPoints(self, player, year=datetime.datetime.now().year):
        points = 0.0
        points += self.rushingYardPoints(player=player,year=year)
        points += player.rushingTDs(year) * self.pointsPerRushingTouchdown
        points += player.rushingTwoPointers(year) * self.pointsPerRushingTwoPointConversion
        return points

    def receivingPoints(self, player, year=datetime.datetime.now().year):
        points = 0.0
        points += self.receivingYardPoints(player=player,year=year)
        points += player.receivingTDs(year) * self.pointsPerReceivingTouchdown
        points += player.receptions(year) * self.pointsPerReception
        points += player.receivingTwoPointers(year) * self.pointsPerReceivingTwoPointConversion
        return points

    def points(self, player, year=datetime.datetime.now().year):
        points = 0.0
        points += self.passingPoints(player=player,year=year)
        points += self.rushingPoints(player=player,year=year)
        points += self.receivingPoints(player=player,year=year)

        # fieldgoal stats needed
        # punt return TDs * 6
        # kick return TDs * 6
        points += player.fumblesLost(year) * self.pointsPerFumblesLost
        points += player.fumbleTDs(year) * self.pointsPerFumblesTouchdown

        return points


class RulesTest(unittest.TestCase):

    def testConstructor(self):
        r = Rules()
        self.assertNotEqual(r, None)

        fbr = FootballRules()
        self.assertNotEqual(fbr, None)

    def testCalculation(self):
        from db.footballdb import FootballPlayerDB
        from sitescraper.nfl.fantasyprosdotcom import FantasyProsDotComScraper

        r = FootballRules()
        fdb = FootballPlayerDB()

        scrape_with_fdb = False

        if scrape_with_fdb:
            from sitescraper.nfl.footballdbdotcom import FootballDBDotComScraper
            fdb.wget([FantasyProsDotComScraper(), FootballDBDotComScraper()])
        else:
            fdb.wget(scrapers=[FantasyProsDotComScraper()])

        for p in ["cam newton - car", "julio jones - atl"]:

            fp = fdb.player[p]
            print str(fp)
            print "Passing Points 2018: " + str(r.passingPoints(fp,2018))
            print "Passing Points 2017: " + str(r.passingPoints(fp,2017))
            print "Passing Points 2016: " + str(r.passingPoints(fp,2016))
            print "Passing Points 2015: " + str(r.passingPoints(fp,2015))
            print "Passing Points 2014: " + str(r.passingPoints(fp,2014))

            this_year = datetime.datetime.now().year
            if fp.gamesPlayed(this_year) != 0:
                print "Points " + str(this_year) + ": " + str(r.points(fp,this_year)/fp.gamesPlayed(this_year))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()