import unittest


class PlayerStrings(object):

    Name = 'name'
    Position = 'position'
    Team = 'team'
    FantasyOwner = 'owner'
    Link = 'link'
    Stats = 'stats'
    GamesPlayed = 'GamesPlayed'
    ProjectedPrefix = 'Projected'

    def __init__(self, prefix=None):
        if prefix is None:
            self.prefix = ""
        else:
            self.prefix = prefix

        self.map = {}
        self.map['gp'] = PlayerStrings.GamesPlayed
        self.map['ggp'] = PlayerStrings.GamesPlayed

    def name(self):
        return PlayerStrings.Name

    def position(self):
        return PlayerStrings.Position

    def team(self):
        return PlayerStrings.Team

    def owner(self):
        return PlayerStrings.FantasyOwner

    def addprefix(self):
        if self.prefix == "":
            return ""
        else:
            return self.prefix + "."

    def link(self, sublink=None):

        if sublink is not None and sublink != "":
            sublink_string = str(sublink) + "."
        else:
            sublink_string = ""

        return self.addprefix() + sublink_string + PlayerStrings.Link

    def stats(self, statstype=None):

        if statstype is not None and statstype != "":
            sublink_string = str(statstype) + "."
        else:
            sublink_string = ""

        return self.addprefix() + sublink_string + PlayerStrings.Stats

    def statString(self,string):
            return self.addprefix() + string

    def projectedString(self,string):
        return self.addprefix() + PlayerStrings.ProjectedPrefix + '.' + string

    def gamesPlayed(self):
        return self.statString(PlayerStrings.GamesPlayed)

    def projectedGamesPlayed(self):
        return self.projectedString(PlayerStrings.GamesPlayed)

    def sanitize(self,stat_name):

        if isinstance(stat_name, list):
            sanitized_list = []
            for stat in stat_name:
                sanitized_list.append(self.sanitize(stat))
            return sanitized_list
        else:
            stat_name = stat_name.lower()
            if stat_name in self.map:
                stat_name = self.map[stat_name]
            return stat_name


class HockeyPlayerStrings(PlayerStrings):

    Goals = "Goals"
    Assists = "Assists"
    Points = "Points"
    Wins = "Wins"
    Ties = "Ties"
    Ties = "Loses"
    Shutouts = "Shutouts"

    ProjectedGoals = PlayerStrings.ProjectedPrefix + Goals
    ProjectedAssists = PlayerStrings.ProjectedPrefix + Assists
    ProjectedWins = PlayerStrings.ProjectedPrefix + Wins
    ProjectedTies = PlayerStrings.ProjectedPrefix + Ties
    ProjectedShutouts = PlayerStrings.ProjectedPrefix + Shutouts

    def __init__(self, prefix=None):
        super(HockeyPlayerStrings, self).__init__(prefix=prefix)
        self.map['g'] = HockeyPlayerStrings.Goals
        self.map['a'] = HockeyPlayerStrings.Assists
        self.map['pts'] = HockeyPlayerStrings.Points
        self.map['w'] = HockeyPlayerStrings.Wins
        self.map['so'] = HockeyPlayerStrings.Shutouts


    def goals(self):
        return self.statString(HockeyPlayerStrings.Goals)

    def projectedGoals(self):
        return self.projectedString(HockeyPlayerStrings.Goals)

    def assists(self):
        return self.statString(HockeyPlayerStrings.Assists)

    def projectedAssists(self):
        return self.projectedString(HockeyPlayerStrings.Assists)

    def points(self):
        return self.statString(HockeyPlayerStrings.Points)

    def projectedPoints(self):
        return self.projectedString(HockeyPlayerStrings.Points)

    def wins(self):
        return self.statString(HockeyPlayerStrings.Wins)

    def projectedWins(self):
        return self.projectedString(HockeyPlayerStrings.Wins)

    def ties(self):
        return self.statString(HockeyPlayerStrings.Ties)

    def projectedTies(self):
        return self.projectedString(HockeyPlayerStrings.Ties)

    def shutouts(self):
        return self.statString(HockeyPlayerStrings.Shutouts)

    def projectedShutouts(self):
        return self.projectedString(HockeyPlayerStrings.Shutouts)

class TestHockeyPlayerStrings(unittest.TestCase):

    def testHockeyPlayerStrings(self):
        s = HockeyPlayerStrings("foo")
        self.assertEqual(s.gamesPlayed(),'foo.GamesPlayed')
        self.assertEqual(s.projectedGamesPlayed(),'foo.Projected.GamesPlayed')
        self.assertEqual(s.wins(),'foo.Wins')
        self.assertEqual(s.projectedWins(),'foo.Projected.Wins')
