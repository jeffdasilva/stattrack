'''
Created on Sep 3, 2016

@author: jdasilva
'''
import unittest

from db.footballdb import FootballPlayerDB
from league import League


class FootballLeague(League):

    def __init__(self, name, db=None, rules=None):

        if db is None:
            db = FootballPlayerDB()
        super(FootballLeague, self).__init__(name, db, rules)

class FootballLeagueTest(unittest.TestCase):

    def testConstructor(self):

        ffl = FootballLeague("test")
        self.assertNotEquals(ffl, None)
        self.assertEquals(ffl.property['isAuctionDraft'], 'false')

        pass


if __name__ == "__main__":
    unittest.main()