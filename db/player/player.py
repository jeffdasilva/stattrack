'''
@author: jdasilva
'''

import datetime
import unittest

from db.player.hdict import HierarchicalDict
from db.player.strings import PlayerStrings


class Player(object):

    es = PlayerStrings()

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
        self.db = None
        assert(self.name != None)

    def __str__(self):

        player_str = '{0: <25}'.format(self.name)

        if self.team is None:
            team_str = "???"
        else:
            team_str = self.team

        player_str += " " + '{0: <5}'.format(team_str)

        player_str += " " + '{0: <6}'.format('/'.join(self.position))

        player_str += " " + '{0: <5}'.format(str(round(self.value(),2)))

        return player_str

    def printAllToString(self):
        playerStr = ""
        if self.name is not None:
            playerStr += "Name: " + self.name + "\n"

        if self.nameAliases is not None and len(self.nameAliases) > 0:
            playerStr += "Aliases: " + self.nameAliases + "\n"

        if self.team is not None:
            playerStr += "Team: " + self.team + "\n"
        else:
            playerStr += "Team: None" + "\n"

        if self.property is not None:
            playerStr += "Properties: " + "\n"
            for prop in self.property:
                playerStr += "  " + prop + ": " + str(self.property[prop]) + "\n"

        return playerStr

    def printAll(self):
        print(self.printAllToString())

    def getProperty(self,statName,return_value_if_none=None):

        if statName is None:
            return return_value_if_none

        elif isinstance(statName,list):
            for stat_i in statName:
                prop = self.getProperty(stat_i)
                if prop is not None:
                    return prop
            return return_value_if_none

        elif statName not in self.property:
            return return_value_if_none

        return self.property[statName].replace(',','')

    def getStat(self, statName, year=datetime.datetime.now().year):
        if str(year) in self.property:
            if statName in self.property[str(year)]:
                stat = self.property[str(year)][statName].replace(',','')
                return stat
        return 0;

    def value(self):
        return 0

    def age(self, year=datetime.datetime.now().year):
        if 'age' in self.property:
            return int(self.property['age'])
        elif 'rotoworld' in self.property:
            age = str(self.property['rotoworld'][1][1]).split(' / ')[0].lstrip('(').rstrip(')')

            try:
                age = int(age)
            except ValueError:
                age = '-'

            return age
        else:
            return '?'

    def draft(self, cost=0, owner=None):
        self.isDrafted = True
        self.cost = cost

        if owner is not None:
            self.property[Player.es.owner()] = owner

    def undraft(self):
        self.isDrafted = False
        self.cost = 0

        if Player.es.owner() in self.property:
            del self.property[Player.es.owner()]

    def ignore(self):
        self.isIgnored = True

    def unignore(self):
        self.isIgnored = False

    def __cmp__(self, other):

        if other is None:
            return 1

        if self.value() > other.value():
            return 1
        elif self.value() < other.value():
            return -1
        else:
            return 0

    def key(self):

        nameToKey = self.name.lower()
        teamToKey = self.team

        for suffix in [" Sr.", " Jr.", " III"]:
            if nameToKey.endswith(suffix.lower()):
                nameToKey = nameToKey.rsplit(suffix.lower(),1)[0]

        if teamToKey == None:
            teamToKey = "unknown"

        teamToKey = teamToKey.lower()

        return str(nameToKey) + " - " + str(teamToKey)

    def team_abbreviate(self,teamname):
        return teamname

    def team_fullname(self,teamname):
        return teamname

    def normalize_playername(self,name):
        return name

    def is_duplicate_playername(self,name):
        return False

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

        if self.property.has_key("isDrafted"):
            self.isDrafted = self.property["isDrafted"]
            del self.property["isDrafted"]

        if self.property.has_key("isIgnored"):
            self.isIgnored = self.property["isIgnored"]
            del self.property["isIgnored"]

        if self.name is not None:
            self.name = self.normalize_playername(self.name)

        if self.team is not None and (self.team.lower() == "unknown" or self.team.lower() == "fa" or self.team == "???"):
            self.team = None

        if self.team is not None:
            self.team = self.team_abbreviate(self.team).upper()

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
        print(p)

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
        print(p.key())
        self.assertEqual(p.key(), "jeff - unknown")

        p = Player(name="Jeff", team="JDS")
        print(p.key())
        self.assertEqual(p.key(), "jeff - jds")

        p = Player(name="JeFF III", team="JdSx")
        print(p.key())
        self.assertEqual(p.key(), "jeff - jdsx")

        p = Player(name="Jeff JR.")
        print(p.key())
        self.assertEqual(p.key(), "jeff - unknown")


if __name__ == '__main__':
    unittest.main()
