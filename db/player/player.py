'''
@author: jdasilva
'''

import unittest

from db.player.hdict import HierarchicalDict

class Player(object):

    def __init__(self, name=None, team=None, properties={}):
        '''
        Constructor
        '''
        self.name = name
        self.nameAliases = []
        self.team = team
        self.position = []
        self.property = HierarchicalDict()
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

        player_str += " " + '{0: <7}'.format(str(self.value()))

        return player_str

    def printAll(self):
        print "Name: " + self.name
        if len(self.nameAliases) > 0:
            print "Aliases: " + self.nameAliases
        print "Team: " + self.team
        print "Properties: "
        for prop in self.property:
            print "  " + prop + ": " + str(self.property[prop])

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

        nameToKey = self.name.lower()
        teamToKey = self.team

        for suffix in [" Jr.", " III"]:
            if nameToKey.endswith(suffix.lower()):
                nameToKey = nameToKey.rsplit(suffix.lower(),1)[0]

        if teamToKey == None:
            teamToKey = "unknown"

        teamToKey = teamToKey.lower()

        return str(nameToKey) + " - " + str(teamToKey)

    def update(self, properties):

        # this dict update needs to get fancier!
        #   ...because if the dict contains a dict then we need to update those
        #      dict's recursively
        self.property.update(properties)

        if self.property.has_key("name"):
            self.name = self.property["name"]
            del self.property["name"]

        if self.property.has_key("team"):
            self.team = self.property["team"]
            del self.property["team"]

        if self.team is not None and (self.team.lower() == "unknown" or self.team.lower() == "FA" or self.team == "???"):
            self.team = None

        if self.team is not None:
            self.team = self.team.upper()

        # ToDo: Move this to Football Class
        if self.team == "JAC":
            self.team = "JAX"

        if self.property.has_key("position"):
            if self.property["position"] not in self.position:
                self.position.append(self.property["position"])
            del self.property["position"]

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

        # note that if you change teams, your key changes
        # playerdb class handles this case in it's add(player) method
        if player.team != None and self.team != player.team:
            self.team = player.team

        for p in player.position:
            if p not in self.position:
                self.position.append(p)

        self.update(player.property)


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
        player_prop["team"] = 'sj'
        player_prop["foo"] = 'bar'

        p = Player(properties=player_prop)
        self.assertEquals(p.team, "SJ")
        self.assertEquals(p.name, "foo")
        self.assertEquals(p.property["foo"],'bar')
        self.assertTrue(not p.property.has_key("name"))
        self.assertTrue(not p.property.has_key("team"))

        player_prop["name"] = 'foo2'
        p.update(player_prop)
        self.assertEquals(p.team, "SJ")
        self.assertEquals(p.name, "foo2")
        self.assertEquals(p.property["foo"],'bar')
        self.assertTrue(not p.property.has_key("name"))
        self.assertTrue(not p.property.has_key("team"))
        self.assertTrue(not p.property.has_key("position"))

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

        self.assertTrue(not p.property.has_key("position"))
        self.assertTrue(not p2.property.has_key("position"))

    def testKeyMethod(self):

        p = Player(name="Jeff")
        print p.key()
        self.assertEqual(p.key(), "jeff - unknown")

        p = Player(name="Jeff", team="JDS")
        print p.key()
        self.assertEqual(p.key(), "jeff - jds")

        p = Player(name="JeFF III", team="JdSx")
        print p.key()
        self.assertEqual(p.key(), "jeff - jdsx")

        p = Player(name="Jeff JR.")
        print p.key()
        self.assertEqual(p.key(), "jeff - unknown")


if __name__ == '__main__':
    unittest.main()
