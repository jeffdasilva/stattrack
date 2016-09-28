
import unittest

from db.hockeydb import HockeyPlayerDB
from league import League


class HockeyLeague(League):

    def __init__(self, name, db=None, rules=None):

        if db is None:
            db = HockeyPlayerDB(name=name)
        super(HockeyLeague, self).__init__(name, db, rules)

class HockeyLeagueTest(unittest.TestCase):

    def testConstructor(self):
        hl = HockeyLeague("test")
        self.assertNotEquals(hl, None)
        self.assertEquals(hl.property['isAuctionDraft'], 'false')


if __name__ == "__main__":
    unittest.main()
