'''
Created on Aug 30, 2015

@author: jdasilva
'''
import unittest
import pickle
import os
import re

class Player(object):

    def __init__(self, name=None, team=None, properties={}):
        '''
        Constructor
        '''
        self.name = name
        self.nameAliases = []
        self.team = team
        self.position = []
        self.prop = {}
        self.isDrafted = False
        self.isIgnored = False
        self.update(properties)
        self.cost = 0
        assert(self.name != None)
        
    def __str__(self):

        player_str = '{0: <20}'.format(self.name)
        player_str += " " + '{0: <5}'.format(self.team) 
        player_str += " " + '{0: <6}'.format('/'.join(self.position))

        if self.prop.has_key("fantasyPoints"):
            player_str += " " + '{0: <8}'.format(str(self.prop["fantasyPoints"]))

        player_str += " " + '{0: <8}'.format(str(self.value()))    
        
        return player_str 

    def value(self):
        return 0

    def draft(self, cost=0):
        self.isDrafted = True
        self.cost=cost

    def undraft(self):
        self.isDrafted = False

    def ignore(self):
        self.isIgnored = True

    def unignore(self):
        self.isIgnored = False

    def __cmp__(self, other):
        if self.value() > other.value():
            return 1
        elif self.value() < other.value():
            return -1
        else:
            return 0

    def key(self):
        if self.team is None:
            return self.name + " - " + "unknown"
        else:
            return self.name + " - " + self.team
    
    def update(self, properties):
        self.prop.update(properties)

        if self.prop.has_key("name"):
            self.name = self.prop["name"]
            del self.prop["name"]

        if self.prop.has_key("team"):
            self.team = self.prop["team"]
            del self.prop["team"]

        if self.prop.has_key("position"):
            if self.prop["position"] not in self.position:
                self.position.append(self.prop["position"])
            del self.prop["position"]

    def merge(self, player):

        if self.name != player.name:
            if player.name not in self.nameAliases:
                self.nameAliases.append(player.name)
        
        for n in player.nameAliases:
            if n not in self.nameAliases:
                self.nameAliases.append(n)

        self.isDrafted = self.isDrafted or player.isDrafted
        self.isIgnored = self.isIgnored or player.isIgnored

        self.cost = max(self.cost, player.cost)

        if player.team != None:
            self.team = player.team
        for p in player.position:
            if p not in self.position:
                self.position.append(p)
        self.update(player.prop)


class PlayerDB(object):
    
    def __init__(self, positionMap={}):
        self.player = {}
        self.positionMap = {"all":["all"]}
        self.positionMap.update(positionMap)
        self.saveFile = os.path.dirname(os.path.abspath(__file__)) + "/data/playerdb.pickle"

    def add(self, player):
        if self.player.has_key(player.key()):
            self.player[player.key()].merge(player)
        else:
            self.player[player.key()] = player

    def save(self):
        with open(self.saveFile, 'wb') as handle:
            pickle.dump(self.player, handle)
    
    def load(self):
        with open(self.saveFile, 'rb') as handle:
            playerData = pickle.load(handle)
        self.update(playerData)

    def update(self, playerData):
        for key in playerData:
            self.add(playerData[key])

    def getRE(self, playerNameREString, position="all", listDrafted=False, listIgnored=False):
        reObj = re.compile(playerNameREString, re.IGNORECASE)
        player_list = []
        for playerObj in self.player.itervalues():

            if not listIgnored and playerObj.isIgnored:
                continue

            if not listDrafted and playerObj.isDrafted:
                continue
            
            match_found = False
            position_to_match = self.positionMap[position]
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

    def get(self, searchString="", position="all", listDrafted=False, listIgnored=False):
        
        if searchString == "":
            searchString = '.*'
        else:
            searchString = '.*' + searchString + '.*'
        
        return self.getRE(searchString, position=position, listDrafted=listDrafted, listIgnored=listIgnored)

    def numberOfPlayersDrafted(self, position="all"):
        plist = self.get(position=position, listDrafted=True)
        
        draft_count = 0
        
        for p in plist:
            if p.isDrafted:
                draft_count += 1
                
        return draft_count
        


class TestPlayer(unittest.TestCase):
    
    def testNoNamePlayer(self):
        try:
            Player()
            self.assertTrue(False)
        except AssertionError:
            pass
            
    def testNamedPlayer(self):
        p = Player("Jeff DaSilva")
        self.assertEquals(p.name, "Jeff DaSilva")

    def testTeamSet(self):
        p = Player(team="NJ", name="foo")
        self.assertEquals(p.team, "NJ")

    def testValueIsZero(self):
        self.assertEquals(Player("zero").value(),0)

    def testNameTeamPropSet(self):
        player_prop = {}
        player_prop["name"] = 'foo'
        player_prop["team"] = 'SJ'
        player_prop["foo"] = 'bar'

        p = Player(properties=player_prop)
        self.assertEquals(p.team, "SJ")
        self.assertEquals(p.name, "foo")
        self.assertEquals(p.prop["foo"],'bar')
        self.assertTrue(not p.prop.has_key("name"))
        self.assertTrue(not p.prop.has_key("team"))

        player_prop["name"] = 'foo2'
        p.update(player_prop)
        self.assertEquals(p.team, "SJ")
        self.assertEquals(p.name, "foo2")
        self.assertEquals(p.prop["foo"],'bar')
        self.assertTrue(not p.prop.has_key("name"))
        self.assertTrue(not p.prop.has_key("team"))
        self.assertTrue(not p.prop.has_key("position"))

    def testPositionFeature(self):
        p = Player("Jeff") 
        self.assertEquals(p.position,[])
        p.position += [ "LW" ]
        self.assertEquals(p.position,["LW"])

        p.update({'position':'RW'})
        self.assertEquals(p.position,["LW","RW"])

        p.update({'position':'G'})
        self.assertEquals(p.position,["LW","RW","G"])

        p.update({'position':'LW'})
        self.assertEquals(p.position,["LW","RW","G"])

        p2 = Player(name="p2", properties={'position':'D'})
        p2.update({'position':'G'})
        self.assertEquals(p2.position,["D","G"])

        p.merge(p2)
        self.assertEquals(p.position,["LW","RW","G","D"])

        self.assertTrue(not p.prop.has_key("position"))
        self.assertTrue(not p2.prop.has_key("position"))

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
        pDB.saveFile = os.path.dirname(os.path.abspath(__file__)) + "/test_myplayerdb.pickle"

        pDB.add(Player("June", "Team June", {"position":"C", "goals":24, "assists":33, "wins":1, "losses":22}))
        pDB.add(Player("Eleanor", "Team June", {"position":"D", "goals":24, "assists":100}))
        pDB.add(Player("June", "Team Stuffins"))
        pDB.add(Player("Sophia", "Team Stuffins"))
        pDB.add(Player("June", "Team June", {"position":"RW", "goals":24, "ties":4}))
        pDB.add(Player("June", "Team June", {"position":"G", "saves":124, "wins":6}))
                
        june = pDB.player[Player("June", "Team June").key()]
        self.assertEquals(june.name,"June")
        self.assertEquals(june.team,"Team June")
        self.assertEquals(june.position,["C","RW","G"])
        self.assertEquals(june.prop["goals"],24)
        self.assertEquals(june.prop["assists"],33)
        self.assertEquals(june.prop["wins"],6)
        self.assertEquals(june.prop["losses"],22)
        self.assertEquals(june.prop["ties"],4)
        self.assertEquals(june.prop["saves"],124)

        pDB.save()
        pDB.load()
        june = pDB.player[Player("June", "Team June").key()]
        self.assertEquals(june.name,"June")
        self.assertEquals(june.team,"Team June")
        self.assertEquals(june.position,["C","RW","G"])
        self.assertEquals(june.prop["goals"],24)
        self.assertEquals(june.prop["assists"],33)
        self.assertEquals(june.prop["wins"],6)
        self.assertEquals(june.prop["losses"],22)
        self.assertEquals(june.prop["ties"],4)
        self.assertEquals(june.prop["saves"],124)
        
        pDB_copy = PlayerDB()
        pDB_copy.saveFile = os.path.dirname(os.path.abspath(__file__)) + "/test_myplayerdb.pickle"
        pDB_copy.load()
        june = pDB_copy.player[Player("June", "Team June").key()]
        self.assertEquals(june.name,"June")
        self.assertEquals(june.team,"Team June")
        self.assertEquals(june.position,["C","RW","G"])
        self.assertEquals(june.prop["goals"],24)
        self.assertEquals(june.prop["assists"],33)
        self.assertEquals(june.prop["wins"],6)
        self.assertEquals(june.prop["losses"],22)
        self.assertEquals(june.prop["ties"],4)
        self.assertEquals(june.prop["saves"],124)
      

if __name__ == '__main__':
    unittest.main()
