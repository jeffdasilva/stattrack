import datetime
import unittest

from db.player.player import Player
from sitescraper.nhl.cbssportsdotcom import NhlCbsSportsDotComSraper
from sitescraper.nhl.tsndotca import TsnDotCaScraper


class HockeyPlayer(Player):

    def __init__(self, name=None, team=None, properties={}):
        super(HockeyPlayer, self).__init__(name=name, team=team, properties=properties)

        #ToDo: a factory creator class should really add these
        self.projected_games_played_attr = TsnDotCaScraper.ProjectedGamesPlayed + NhlCbsSportsDotComSraper.ProjectedGamesPlayed
        self.projected_goals_attr = TsnDotCaScraper.ProjectedGoals + NhlCbsSportsDotComSraper.ProjectedGoals
        self.projected_assists_attr = TsnDotCaScraper.ProjectedAssists + NhlCbsSportsDotComSraper.ProjectedAssists
        self.projected_wins_attr = TsnDotCaScraper.ProjectedWins + NhlCbsSportsDotComSraper.ProjectedWins
        self.projected_ties_attr = TsnDotCaScraper.ProjectedTies + NhlCbsSportsDotComSraper.ProjectedTies
        self.projected_shutouts_attr = TsnDotCaScraper.ProjectedShutouts + NhlCbsSportsDotComSraper.ProjectedShutouts


    def normalize_playername(self,name):

        nameNomalizeMap = { \
            'Alex Ovechkin':'Alexander Ovechkin',
            'Mike Cammalleri':'Michael Cammalleri'
        }

        if name in nameNomalizeMap:
            return nameNomalizeMap[name]
        else:
            return super(HockeyPlayer,self).normalize_playername(name)


    def team_abbreviate(self,teamname):

        if teamname is None:
            raise ValueError('ERROR: invalid team name ' + teamname)

        teamname = teamname.lower()
        teamname = teamname.replace('.','')

        teamNameAbbreviateMap = { \
        'anaheim ducks':'ana', 'arizona coyotes':'ari', 'boston bruins':'bos', \
        'buffalo sabres':'buf', 'calgary flames':'cgy', 'carolina hurricanes':'car', \
        'chicago blackhawks':'chi', 'colorado avalanche':'col', 'columbus blue jackets':'clb', \
        'dallas stars':'dal', 'detroit red wings':'det', 'edmonton oilers':'edm', \
        'florida panthers':'fla', 'los angeles kings':'la', 'minnesota wild':'min', \
        'montreal canadiens':'mon', 'nashville predators':'nsh', 'new jersey devils':'nj', \
        'new york islanders':'nyi', 'new york rangers':'nyr', 'philadelphia flyers':'phi', \
        'pittsburgh penguins':'pit', 'ottawa senators':'ott', 'san jose sharks':'sj', \
        'st louis blues':'stl', 'tampa bay lightning':'tb',  'toronto maple leafs':'tor', \
        'vancouver canucks':'van', 'washington capitals':'was', 'winnipeg jets':'wpg' \
        }

        abbreviated_teamnames = teamNameAbbreviateMap.values()

        for team in teamNameAbbreviateMap.keys():
            # Toronto, Columbus, and Detroit are special cases because their team name
            # has a space
            if team == 'toronto maple leafs' or team == 'columbus blue jackets' or \
                team == 'detroit red wings':
                city,name = team.split(' ',1)
            else:
                city,name = team.rsplit(' ',1)

            if city != "new york":
                teamNameAbbreviateMap[city] = teamNameAbbreviateMap[team]

            teamNameAbbreviateMap[name] = teamNameAbbreviateMap[team]

        teamNameAbbreviateMap['ny islanders'] = teamNameAbbreviateMap['new york islanders']
        teamNameAbbreviateMap['ny rangers'] = teamNameAbbreviateMap['new york rangers']

        for team in abbreviated_teamnames:
            teamNameAbbreviateMap[team] = team

        if teamname not in teamNameAbbreviateMap:
            raise ValueError('ERROR: invalid team name ' + teamname)

        return teamNameAbbreviateMap[teamname]

    def goals(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedGoals()
        else:
            return 0

    def projectedGoals(self):
        return float(self.getProperty(self.projected_goals_attr,0))

    def assists(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedAssists()
        else:
            return 0

    def projectedAssists(self):
        return float(self.getProperty(self.projected_assists_attr,0))

    def goaltenderWins(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedGoaltenderWins()
        else:
            return 0

    def projectedGoaltenderWins(self):
        return float(self.getProperty(self.projected_wins_attr,0))

    def goaltenderTies(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedGoaltenderTies()
        else:
            return 0

    def projectedGoaltenderTies(self):
        return float(self.getProperty(self.projected_ties_attr,0))


    def goaltenderShutOuts(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedGoaltenderShutOuts()
        else:
            return 0

    def projectedGoaltenderShutOuts(self):
        return float(self.getProperty(self.projected_shutouts_attr,0))

    def gamesPlayed(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedGamesPlayed()
        else:
            return 0

    def projectedGamesPlayed(self):
        return float(self.getProperty(self.projected_games_played_attr,0))

    def points(self,year=datetime.datetime.now().year):
        return self.goals(year) + self.assists(year) + self.goaltenderWins(year)*2 + self.goaltenderTies(year) + self.goaltenderShutOuts(year)*4

    def pointsPerGame(self,year=datetime.datetime.now().year):
        if self.gamesPlayed(year) == 0:
            return 0.0
        else:
            return self.points(year)/self.gamesPlayed(year)

    def value(self):
        if 'G' in self.position:
            value = self.points() / 82
        else:
            value = self.pointsPerGame()
        return value


class TestHockeyPlayer(unittest.TestCase):

    def testHockeyPlayer(self):

        p = HockeyPlayer(name="JDS")
        self.assertNotEqual(p, None)
        self.assertEqual(p.pointsPerGame(),0)

        p.property[p.projected_games_played_attr[-1]] = "10"
        self.assertEqual(p.pointsPerGame(),0)

        p.property[p.projected_assists_attr[0]] = "5"
        self.assertEqual(p.pointsPerGame(),0.5)

    def testTeamAbbreviate(self):
        p = HockeyPlayer(name="noname")
        self.assertEqual(p.team_abbreviate('Pittsburgh'),'pit')
        self.assertEqual(p.team_abbreviate('.P.I.T.'),'pit')

    def testGoalieAbbreviate(self):

        p = HockeyPlayer(name='goalburg')
        print p.projected_shutouts_attr

        self.assertEqual(p.pointsPerGame(),0)

        p.property[p.projected_games_played_attr[-1]] = "10"
        self.assertEqual(p.pointsPerGame(),0)

        p.property[p.projected_wins_attr[-1]] = "5"
        self.assertEqual(p.pointsPerGame(),1.0)

        p.property[p.projected_shutouts_attr[-1]] = "10"
        self.assertEqual(p.pointsPerGame(),5.0)






if __name__ == '__main__':
    unittest.main()
