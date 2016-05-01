'''
@author: jdasilva
'''
import os
import pickle
import re
import unittest

from db.player.player import Player


class PlayerDB(object):

    def __init__(self, positionMap={}):
        self.player = {}
        self.positionMap = {"all":["all"]}
        self.positionMap.update(positionMap)
        self.saveFile = os.path.dirname(os.path.abspath(__file__)) + "/../data/playerdb.pickle"




    def add(self, player):
        if self.player.has_key(player.key()):
            playerKeyIn = player.key()
            self.player[playerKeyIn].merge(player)
            if self.player[playerKeyIn].key() != playerKeyIn:
                player = self.player[playerKeyIn]
                del self.player[playerKeyIn]
                self.player[player.key()] = player
            return

        playerMatchByName = self.get(searchString=player.name, listDrafted=True, listIgnored=True)
        if len(playerMatchByName) == 1:
            #print "Looking for (by name) " + player.name + " " + str(player.team)
            #print "Found (by name) " + playerMatchByName[0].name + " " + str(playerMatchByName[0].team)
            playerKeyIn = playerMatchByName[0].key()
            self.player[playerKeyIn].merge(player)
            if self.player[playerKeyIn].key() != playerKeyIn:
                #print "  Changing Teams!!!"
                player = self.player[playerKeyIn]
                del self.player[playerKeyIn]
                self.player[player.key()] = player
            return

        self.player[player.key()] = player

    def save(self):
        if not os.path.exists(os.path.dirname(self.saveFile)):
            os.makedirs(os.path.dirname(self.saveFile))

        with open(self.saveFile, 'wb') as handle:
            pickle.dump(self.player, handle)

    def load(self):
        if os.path.isfile(self.saveFile):
            with open(self.saveFile, 'rb') as handle:
                playerData = pickle.load(handle)
                self.update(playerData)

    def update(self, playerData):
        for key in playerData:
            self.add(playerData[key])

    def getWithRegularExpression(self, playerNameREString, position="all", team="all", listDrafted=False, listIgnored=False):
        reObj = re.compile(playerNameREString, re.IGNORECASE)
        player_list = []
        for playerObj in self.player.itervalues():

            if not listIgnored and playerObj.isIgnored:
                continue

            if not listDrafted and playerObj.isDrafted:
                continue

            match_found = False
            if self.positionMap.has_key(position.lower()):
                position_to_match = self.positionMap[position.lower()]
            else:
                position_to_match = [ position ]

            for pos_i in position_to_match:
                if pos_i == "all":
                    match_found = True
                    break
                for pos_j in playerObj.position:
                    if pos_i == pos_j:
                        match_found = True
                        break

            if not match_found:
                continue

            if reObj.match(playerObj.name):
                player_list.append(playerObj)

        player_list.sort(reverse=True)
        return player_list

    def get(self, searchString="", position="all", team="all", listDrafted=False, listIgnored=False):

        if searchString == "":
            searchString = '.*'
        else:
            searchString = '.*' + searchString + '.*'

        return self.getWithRegularExpression(searchString, position=position, team=team, listDrafted=listDrafted, listIgnored=listIgnored)

    def numberOfPlayersDrafted(self, position="all"):
        plist = self.get(position=position, listDrafted=True)

        draft_count = 0

        for p in plist:
            if p.isDrafted:
                draft_count += 1

        return draft_count

class TestPlayerDB(unittest.TestCase):

    def testPlayerGet(self):
        pDB = PlayerDB()

        self.assertEquals(pDB.numberOfPlayersDrafted(), 0)

        pDB.add(Player("June"))
        pl = pDB.get("Ju")
        self.assertEquals(len(pl),1)
        print pl[0].name
        pDB.add(Player("JuneBug"))
        pDB.add(Player("Michelle"))
        pDB.add(Player("Sophia"))
        pDB.add(Player("Michelle C"))
        pDB.add(Player("Sophia M"))
        self.assertEquals(len(pDB.get("June")),2)
        self.assertEquals(len(pDB.get("jUnE")),2)
        self.assertEquals(len(pDB.get("uN")),2)
        self.assertEquals(len(pDB.get("i")),4)
        self.assertEquals(len(pDB.get("OPHIA")),2)

        pDB.get("JuneBug")[0].draft()
        self.assertEquals(pDB.numberOfPlayersDrafted(), 1)


        pass

    def testPlayerDBBasic(self):
        pDB = PlayerDB()
        pDB.saveFile = os.path.dirname(os.path.abspath(__file__)) + "/../data/test_myplayerdb.pickle"

        pDB.add(Player("June", "Team-June", {"position":"C", "goals":24, "assists":33, "wins":1, "losses":22}))
        pDB.add(Player("Eleanor", "Team-June", {"position":"D", "goals":24, "assists":100}))
        pDB.add(Player("June", "Team Stuffins"))
        pDB.add(Player("Sophia", "Team Stuffins"))
        pDB.add(Player("June", "Team-June", {"position":"RW", "goals":24, "ties":4}))
        pDB.add(Player("June", "Team-June", {"position":"G", "saves":124, "wins":6}))

        june = pDB.player[Player("June", "Team-June").key()]
        print june
        self.assertEquals(june.name,"June")
        self.assertEquals(june.team,"TEAM-JUNE")
        self.assertEquals(june.position,["C","RW","G"])
        self.assertEquals(june.property["goals"],24)
        self.assertEquals(june.property["assists"],33)
        self.assertEquals(june.property["wins"],6)
        self.assertEquals(june.property["losses"],22)
        self.assertEquals(june.property["ties"],4)
        self.assertEquals(june.property["saves"],124)

        pDB.save()
        pDB.load()
        june = pDB.player[Player("June", "Team-June").key()]
        self.assertEquals(june.name,"June")
        self.assertEquals(june.team,"TEAM-JUNE")
        self.assertEquals(june.position,["C","RW","G"])
        self.assertEquals(june.property["goals"],24)
        self.assertEquals(june.property["assists"],33)
        self.assertEquals(june.property["wins"],6)
        self.assertEquals(june.property["losses"],22)
        self.assertEquals(june.property["ties"],4)
        self.assertEquals(june.property["saves"],124)

        pDB_copy = PlayerDB()
        pDB_copy.saveFile = os.path.dirname(os.path.abspath(__file__)) + "/../data/test_myplayerdb.pickle"
        pDB_copy.load()
        pDB_copy.saveFile = os.path.dirname(os.path.abspath(__file__)) + "/../data/test_myplayerdb2.pickle"
        june = pDB_copy.player[Player("June", "Team-June").key()]
        self.assertEquals(june.name,"June")
        self.assertEquals(june.team,"TEAM-JUNE")
        self.assertEquals(june.position,["C","RW","G"])
        self.assertEquals(june.property["goals"],24)
        self.assertEquals(june.property["assists"],33)
        self.assertEquals(june.property["wins"],6)
        self.assertEquals(june.property["losses"],22)
        self.assertEquals(june.property["ties"],4)
        self.assertEquals(june.property["saves"],124)
