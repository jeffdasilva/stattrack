
import os
import unittest

from db.player.hockey import HockeyPlayer
from db.playerdb import PlayerDB


class HockeyPlayerDB(PlayerDB):

    def __init__(self,name):

        pmap = {}
        pmap["forward"] = [ "F", "RW", "LW", "C" ]
        pmap["f"] = pmap["forward"]
        pmap["center"] = [ "C" ]
        pmap["centre"] = pmap["center"]
        pmap["c"] = pmap["center"]
        pmap["lw"] = [ "LW" ]
        pmap["rw"] = [ "RW" ]
        pmap["defence"] = [ "D" ]
        pmap["defense"] = [ "D" ]
        pmap["def"] = [ "D" ]
        pmap["d"] = [ "D" ]

        super(HockeyPlayerDB, self).__init__(name=name, positionMap=pmap)

    def wget(self, scrapers=[]):
        for s in scrapers:
            data = s.scrape()
            for player_prop in data:
                player = HockeyPlayer(properties=player_prop)
                self.add(player)


class TesthockeyPlayer(unittest.TestCase):

    def testNewhockeyPlayer(self):
        hp = HockeyPlayer(name="Jeff", team="TOR", properties={"position":"D","foo":"bar","name":"DaSilva"})
        self.assertEquals(hp.name,"DaSilva")
        self.assertEquals(hp.team,"TOR")
        self.assertEquals(hp.position,["D"])
        self.assertEquals(hp.property["foo"],"bar")


class TesthockeyPlayerDB(unittest.TestCase):

    def testNewhockeyPlayerDB(self):
        hdb = HockeyPlayerDB("test_hockeydb")
        self.assertTrue(len(hdb.positionMap.keys()) > 5)
        self.assertEquals(hdb.positionMap["forward"],[ "F", "RW", "LW", "C" ])
        pass

    def testSaveFile(self):
        hdb = HockeyPlayerDB("HockeyDBTest")
        self.assertEquals(hdb.saveFile, os.path.dirname(os.path.abspath(__file__)) + "/../data/HockeyDBTest_playerdb.pickle")


if __name__ == '__main__':
    unittest.main()
