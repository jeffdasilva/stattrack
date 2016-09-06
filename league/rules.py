'''
Created on Sep 5, 2016

@author: jdasilva
'''
import unittest


class Rules(object):
    def __init__(self):
        pass

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

        self.pointsPerCompletion = 0.0
        self.pointsPerIncompletePass = 0.0
        self.pointsPerPassingYards = [ (0,1/25), (300,2/25), (350,4/25), (400,6/25) ]
        self.pointsPerPassingTouchdown = 4
        self.pointsPerInterception = -1
        self.pointsPerSack = 0
        self.pointsPerRushingAttempt = 0
        self.pointsPerRushingYard = [ (0,1/10), (100,2/10), (150,4/10), (200,6/10) ]
        self.pointsPerRushingTouchdown = 6
        self.pointsPerReception = 0
        self.pointsPerReceivingYard = [ (0,1/10), (100,2/10), (150,4/10), (200,6/10) ]
        self.pointsPerReceivingTouchdown = 6
        self.pointsPerReturnYard = [ (0,1/20), (100,3/20), (200,6/20) ]
        self.pointsPerReturnTouchdown = 6
        self.pointsPerTwoPointConversion = 2
        self.pointsPerFumble = 0
        self.pointsPerFumblesLost = -2
        self.pointsPerPickSixesThrown = 0
        self.pointsPerFortyPlusYardCompletion = 0
        self.pointsPerFortyPlusYardPassingTouchdown = 0
        self.pointsPerFortyPlusYardRun = 0
        self.pointsPerFortyPlusYardRushingTouchdown = 0
        self.pointsPerFortyPlusYardReception = 0
        self.pointsPerFortyPlusYardReceivingTouchdowns = 0


class RulesTest(unittest.TestCase):

    def testConstructor(self):
        r = Rules()
        self.assertNotEqual(r, None)

        fbr = FootballRules()
        self.assertNotEqual(fbr, None)



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()