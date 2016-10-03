import unittest


class PlayerStrings(object):

    Name = 'name'
    Position = 'position'
    Team = 'team'
    FantasyOwner = 'owner'
    Link = 'link'
    GamesPlayed = 'GamesPlayed'
    ProjectedPrefix = 'Projected'

    def __init__(self, prefix=None):
        if prefix is None:
            self.prefix = ""
        else:
            self.prefix = prefix

        self.map = {}

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

    def link(self):
        return self.addprefix() + PlayerStrings.Link

    def statString(self,string):
            return self.addprefix() + string

    def projectedString(self,string):
        return self.addprefix() + PlayerStrings.ProjectedPrefix + '.' + string

    def gamesPlayed(self):
        return self.statString(PlayerStrings.GamesPlayed)

    def projectedGamesPlayed(self):
        return self.projectedString(PlayerStrings.GamesPlayed)

    def sanitize(self,stat_name):

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
    Shutouts = "Shutouts"

    ProjectedGoals = PlayerStrings.ProjectedPrefix + Goals
    ProjectedAssists = PlayerStrings.ProjectedPrefix + Assists
    ProjectedWins = PlayerStrings.ProjectedPrefix + Wins
    ProjectedTies = PlayerStrings.ProjectedPrefix + Ties
    ProjectedShutouts = PlayerStrings.ProjectedPrefix + Shutouts

    def __init__(self, prefix=None):
        super(HockeyPlayerStrings, self).__init__(prefix=prefix)
        pass

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
