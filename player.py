'''
Created on Aug 30, 2015

@author: jdasilva
'''
import unittest

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
        self.cost = 0
        self.update(properties)       
        assert(self.name != None)
        
    def __str__(self):

        player_str = '{0: <20}'.format(self.name)
        
        if self.team is None:
            team_str = "???"
        else:
            team_str = self.team 
        
        player_str += " " + '{0: <5}'.format(team_str)
         
        player_str += " " + '{0: <6}'.format('/'.join(self.position))

        if self.prop.has_key("fantasyPoints"):
            player_str += " " + '{0: <8}'.format(str(self.prop["fantasyPoints"]))

        player_str += " " + '{0: <8}'.format(str(self.value()))    
        
        return player_str 

    def value(self):
        return 0

    def draft(self, cost=0):
        self.isDrafted = True
        self.cost = cost

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
            
        if self.team is not None and (self.team.lower() == "unknown" or self.team.lower() == "FA" or self.team == "???"):
            self.team = None

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
        print p

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

      

if __name__ == '__main__':
    unittest.main()
