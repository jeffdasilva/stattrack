'''
Created on Sep 5, 2016

@author: jdasilva
'''
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
        self.pointsPerGoalieShutout = 4


class FootballRules(Rules):

    def __init__(self):
        super(FootballRules, self).__init__()

        self.numTeams = 10
        self.numQB = 2
        self.numRB = 3
        self.numWR = 4
        self.numTE = 0
        self.numDEF = 0
        numStarters = self.numQB + self.numRB + self.numWR + self.numTE + self.numDEF
        self.numReserves = 14 - numStarters

        #################################################
        # Passing
        self.pointsPerCompletion = 0.0
        self.pointsPerIncompletePass = 0.0
        self.pointsPerPassingYards = [ (0,1.0/25), (300,2.0/25), (350,4.0/25), (400,6.0/25) ]
        self.pointsPerPassingTouchdown = 4
        self.pointsPerInterception = -1
        self.pointsPerSack = 0
        self.pointsPerPassingTwoPointConversion = 0

        # Rushing
        self.pointsPerRushingAttempt = 0
        self.pointsPerRushingYard = [ (0,1.0/10), (100,2.0/10), (150,4.0/10), (200,6.0/10) ]
        self.pointsPerRushingTouchdown = 6
        self.pointsPerRushingTwoPointConversion = 0

        # Receiving
        self.pointsPerReception = 0
        self.pointsPerReceivingYard = [ (0,1.0/10), (100,2.0/10), (150,4.0/10), (200,6.0/10) ]
        self.pointsPerReceivingTouchdown = 6
        self.pointsPerReceivingTwoPointConversion = 0

        # Special Teams
        self.pointsPerReturnYard = [ (0,1.0/20), (100,3.0/20), (200,6.0/20) ]
        self.pointsPerReturnTouchdown = 6
        self.pointsPerTwoPointConversion = 2
        self.pointsPerFumble = 0
        self.pointsPerFumblesLost = -2

        # Other
        self.pointsPerPickSixesThrown = 0
        self.pointsPerFortyPlusYardCompletion = 0
        self.pointsPerFortyPlusYardPassingTouchdown = 0
        self.pointsPerFortyPlusYardRun = 0
        self.pointsPerFortyPlusYardRushingTouchdown = 0
        self.pointsPerFortyPlusYardReception = 0
        self.pointsPerFortyPlusYardReceivingTouchdowns = 0
        #################################################


    def passingYardPoints(self, player, year=datetime.datetime.now().year):

        gamesPlayed = player.gamesPlayed(year)
        if gamesPlayed == 0:
            return 0.0

        points = 0.0

        passingYardsForYear = player.passingYards(year)
        avgPassingYardsPerGame = passingYardsForYear / player.gamesPlayed(year)

        # work in progress
        #print str(avgPassingYardsPerGame)
        #print str(sorted(self.pointsPerPassingYards, reverse=True))

        # do the simplest thing for now
        points += (self.pointsPerPassingYards[0][1] * avgPassingYardsPerGame) * gamesPlayed

        return points

    def passingPoints(self, player, year=datetime.datetime.now().year):
        points = 0.0
        points += player.passingTDs(year) * (self.pointsPerPassingTouchdown)
        points += self.passingYardPoints(player=player,year=year)
        points += player.passingInterceptionsThrown(year) * (self.pointsPerInterception)
        points += player.passingTwoPointers(year) * (self.pointsPerTwoPointConversion)
        return points

    def points(self, player, year=datetime.datetime.now().year):

        points = 0.0
        points += self.passingPoints(player=player,year=year)

        points += player.rushingTDs(year) * (6)
        points += player.rushingYards(year) * (0.1)
        points += player.rushingTwoPointers(year) * (2)
        points += player.receivingTDs(year) * (6)
        points += player.receivingYards(year) * (0.1)
        points += player.receptions(year) * (0.5)
        points += player.receivingTwoPointers(year) * (2)
        # fieldgoal stats needed
        # punt return TDs * 6
        # kick return TDs * 6
        points += player.fumblesLost(year) * (-2)
        points += player.fumbleTDs(year) * (6)

        return points




class RulesTest(unittest.TestCase):

    def testConstructor(self):
        r = Rules()
        self.assertNotEqual(r, None)

        fbr = FootballRules()
        self.assertNotEqual(fbr, None)

    def testCalculation(self):
        from db.footballdb import FootballPlayerDB

        r = FootballRules()
        fdb = FootballPlayerDB()
        fdb.wget()
        fp = fdb.player["cam newton - car"]
        print str(fp)
        print "Passing Points 2016: " + str(r.passingPoints(fp,2016))
        print "Passing Points 2015: " + str(r.passingPoints(fp,2015))
        print "Passing Points 2014: " + str(r.passingPoints(fp,2014))




if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()