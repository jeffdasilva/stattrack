'''
Created on Sep 3, 2016

@author: jdasilva
'''
import unittest

from db.footballdb import FootballPlayerDB
from league import League


class FantasyFootballLeague(League):
    
    def __init__(self, name, db=None, rules=None):
            
        if db is None:
            db = FootballPlayerDB()
        super(FantasyFootballLeague, self).__init__(name, db, rules)

class FantasyFootballLeagueTest(unittest.TestCase):

    def testConstructor(self):
        
        ffl = FantasyFootballLeague("test")
        self.assertNotEquals(ffl, None)
        
        pass


if __name__ == "__main__":
    unittest.main()