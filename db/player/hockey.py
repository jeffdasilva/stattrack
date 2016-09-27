import datetime
import unittest

from db.player.player import Player


class HockeyPlayer(Player):

    def __init__(self, name=None, team=None, properties={}):
        super(HockeyPlayer, self).__init__(name=name, team=team, properties=properties)

    def points(self,year=datetime.datetime.now().year):
        return 0.0

    def pointsPerGame(self,year=datetime.datetime.now().year):
        if self.gamesPlayed(year) == 0:
            return 0.0
        else:
            return self.points(year)/self.gamesPlayed(year)

    def value(self):
        return 0.0


class TestHockeyPlayer(unittest.TestCase):

    def testHockeyPlayer(self):
        p = HockeyPlayer(name="JDS")
        self.assertNotEqual(p, None)

if __name__ == '__main__':
    unittest.main()
