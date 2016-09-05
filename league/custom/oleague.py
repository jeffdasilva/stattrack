'''
Created on Sep 5, 2016

@author: jdasilva
'''

import unittest

from db.footballdb import FootballPlayerDB
from league.football import FootballLeague


class OLeagueFootballLeague(FootballLeague):

    def __init__(self):

        name = "O-League"
        rules = None
        db = FootballPlayerDB(name)
        super(OLeagueFootballLeague, self).__init__(name, db, rules)
        self.property['isAuctionDraft'] = 'true'


class OLeagueFootballLeagueTest(unittest.TestCase):

    def testConstructor(self):

        ffl = OLeagueFootballLeague()
        self.assertNotEquals(ffl, None)
        self.assertEquals(ffl.property['isAuctionDraft'], 'true')
        self.assertEquals(ffl.name,"O-League")
        self.assertEquals(ffl.db.league,"O-League")

        pass


if __name__ == "__main__":
    unittest.main()