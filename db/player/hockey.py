import datetime
import unittest

from db.player.player import Player
from sitescraper.nhl.tsndotca import TsnDotCaScraper


class HockeyPlayer(Player):

    def __init__(self, name=None, team=None, properties={}):
        super(HockeyPlayer, self).__init__(name=name, team=team, properties=properties)

        #ToDo: a factory creator class should really add these
        '''
        # DON'T TRUST CBS PROJECTIONS! THEY'RE PRETTY BAD AND THOSE ARE PROJECTIONS MOST GM'S WILL USE
        # [SHUTOUTS ARE THE EXCEPTION]
        self.projected_games_played_attr = TsnDotCaScraper.ProjectedGamesPlayed + NhlCbsSportsDotComSraper.ProjectedGamesPlayed
        self.projected_goals_attr = TsnDotCaScraper.ProjectedGoals + NhlCbsSportsDotComSraper.ProjectedGoals
        self.projected_assists_attr = TsnDotCaScraper.ProjectedAssists + NhlCbsSportsDotComSraper.ProjectedAssists
        self.projected_wins_attr = TsnDotCaScraper.ProjectedWins + NhlCbsSportsDotComSraper.ProjectedWins
        self.projected_ties_attr = TsnDotCaScraper.ProjectedTies + NhlCbsSportsDotComSraper.ProjectedTies
        self.projected_shutouts_attr = TsnDotCaScraper.ProjectedShutouts + NhlCbsSportsDotComSraper.ProjectedShutouts
        '''
        self.projected_games_played_attr = TsnDotCaScraper.ProjectedGamesPlayed
        self.projected_goals_attr = TsnDotCaScraper.ProjectedGoals
        self.projected_assists_attr = TsnDotCaScraper.ProjectedAssists
        self.projected_wins_attr = TsnDotCaScraper.ProjectedWins
        self.projected_ties_attr = TsnDotCaScraper.ProjectedTies
        self.projected_shutouts_attr = TsnDotCaScraper.ProjectedShutouts


    def __str__(self):

        player_str = Player.__str__(self)

        player_str += "   | " + '{0: <9}'.format(str(round(self.projectedPointsPerGame(),2))
                                    + "(" +  str(self.gamesPlayed()) + ") " ) + "|"

        for year in ['2016','2015','2014']:
            player_str += " " + '{0: <9}'.format(str(round(self.pointsPerGame(year=year),2)) \
                                    + "(" +  str(self.gamesPlayed(year=year)) + ") " ) + "|"

        return player_str


    def normalize_playername(self,name):

        nameNomalizeMap = { \
            'Alex Ovechkin':'Alexander Ovechkin',
            'Mike Cammalleri':'Michael Cammalleri',
            'Mitch Marner':'Mitchell Marner',
            'Oskar Klefbom':'Oscar Klefbom'
        }

        if name in nameNomalizeMap:
            return nameNomalizeMap[name]
        else:
            return super(HockeyPlayer,self).normalize_playername(name)

    def getStat(self, statName, year=datetime.datetime.now().year):

        if not 'cbssports.stats' in self.property:
            return 0

        if str(year) in self.property['cbssports.stats']:
            if statName in self.property['cbssports.stats'][str(year)]:
                stat = self.property['cbssports.stats'][str(year)][statName].replace(',','')
                return stat
        return 0;

    def team_abbreviate(self,teamname):

        if teamname is None:
            raise ValueError('ERROR: invalid team name ' + teamname)

        teamname = teamname.strip()
        teamname = teamname.lower()
        teamname = teamname.replace('.','')

        teamNameAbbreviateMap = { \
        'anaheim ducks':'ana', 'arizona coyotes':'ari', 'boston bruins':'bos', \
        'buffalo sabres':'buf', 'calgary flames':'cgy', 'carolina hurricanes':'car', \
        'chicago blackhawks':'chi', 'colorado avalanche':'col', 'columbus blue jackets':'clb', \
        'dallas stars':'dal', 'detroit red wings':'det', 'edmonton oilers':'edm', \
        'florida panthers':'fla', 'las vegas golden knights':'lv', 'los angeles kings':'la', \
        'minnesota wild':'min', 'montreal canadiens':'mon', 'nashville predators':'nsh', \
        'new jersey devils':'nj', 'new york islanders':'nyi', 'new york rangers':'nyr', \
        'philadelphia flyers':'phi', 'pittsburgh penguins':'pit', 'ottawa senators':'ott', \
        'san jose sharks':'sj', 'st louis blues':'stl', 'tampa bay lightning':'tb', \
        'toronto maple leafs':'tor', 'vancouver canucks':'van', 'washington capitals':'was', \
        'winnipeg jets':'wpg' \
        }

        abbreviated_teamnames = teamNameAbbreviateMap.values()

        for team in teamNameAbbreviateMap.keys():
            # Toronto, Columbus, and Detroit are special cases because their team name
            # has a space
            if team == 'toronto maple leafs' or team == 'columbus blue jackets' or \
                team == 'detroit red wings':
                city,name = team.split(' ',1)
            elif team == 'las vegas golden knights':
                city = 'las vegas'
                name = 'golden knights'
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
            raise ValueError('ERROR: invalid team name: ' + teamname)

        return teamNameAbbreviateMap[teamname]

    def goals(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedGoals()
        else:
            return float(self.getStat("Goals",year))

    def projectedGoals(self):
        #return float(self.getProperty(self.projected_goals_attr,0))
        return float(self.getProperty(TsnDotCaScraper.ProjectedGoals,0))

    def assists(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedAssists()
        else:
            return float(self.getStat("Assists",year))

    def projectedAssists(self):
        #return float(self.getProperty(self.projected_assists_attr,0))
        return float(self.getProperty(TsnDotCaScraper.ProjectedAssists,0))

    def goaltenderWins(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedGoaltenderWins()
        else:
            return float(self.getStat("Wins",year))

    def projectedGoaltenderWins(self):
        try:
            #return float(self.getProperty(self.projected_wins_attr,0))
            return float(self.getProperty(TsnDotCaScraper.ProjectedWins,0))
        except ValueError:
            #print("WARNING: projectedGoaltenderWins=" + str(self.getProperty(self.projected_wins_attr,0)))
            return 0

    def goaltenderTies(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedGoaltenderTies()
        else:
            return float(self.getStat("Ties",year))

    def projectedGoaltenderTies(self):
        return float(self.getProperty(TsnDotCaScraper.ProjectedTies,0))

    def goaltenderShutOuts(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedGoaltenderShutOuts()
        else:
            return float(self.getStat("Shutouts",year))

    def projectedGoaltenderShutOuts(self):
        try:
            #return float(self.getProperty(self.projected_shutouts_attr,0))
            return float(self.getProperty(TsnDotCaScraper.ProjectedShutouts,0))
        except ValueError:
            return 0

    def gamesPlayed(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedGamesPlayed()
        else:
            return int(self.getStat("GamesPlayed",year))

    def projectedGamesPlayed(self):
        try:
            #return float(self.getProperty(self.projected_games_played_attr,0))
            return float(self.getProperty(TsnDotCaScraper.ProjectedGamesPlayed,0))
        except ValueError:
            return 0

    def points(self,year=datetime.datetime.now().year):
        return self.goals(year) + self.assists(year) + self.goaltenderWins(year)*2 + self.goaltenderTies(year) + self.goaltenderShutOuts(year)*4

    def projectedPoints(self,year=datetime.datetime.now().year):

        #print(year)
        #print(self.projectedGoals())
        #print(self.projectedAssists())
        #print(self.projectedGoaltenderWins())
        #print(self.projectedGoaltenderTies())
        #print(self.projectedGoaltenderShutOuts())

        return self.projectedGoals() + self.projectedAssists() + self.projectedGoaltenderWins()*2 + \
            self.projectedGoaltenderTies() + self.projectedGoaltenderShutOuts()*4

    def pointsPerGame(self,year=datetime.datetime.now().year):
        if self.gamesPlayed(year) == 0:
            return 0.0
        else:
            if 'G' in self.position:
                return self.points(year)/82
            else:
                return self.points(year)/self.gamesPlayed(year)

    def projectedPointsPerGame(self):
        if self.projectedGamesPlayed() == 0:
            return 0.0
        else:
            if 'G' in self.position:
                return self.projectedPoints()/82
            else:
                return self.projectedPoints()/self.projectedGamesPlayed()

    def value(self):
        if 'G' in self.position:
            value = self.points() / 82
        else:
            value = self.pointsPerGame()

        '''
        if 'G' in self.position:
            value = value * 0.85
        elif 'D' in self.position:
            value = value * 1.4
        '''

        '''
        if self.age() != '?':
            # this if is is for keeper leagues (younger players are more valuable
            # use a linear function given age (A) as input find multiplier (F)
            #  - if a player is 18 years old (A_1 = 18), then use multiplier 1.2X (F_1 = 1.2)
            #  - if a player is 40 years old (A_2 = 40), then use multiplier 0.8X (F_2 = 0.8)
            # and now solve (for x & y) the generic linear solution to F = Ax + y
            A_1 = 20
            F_1 = 1.1
            A_2 = 37
            F_2 = 0.9
            x = (F_1 - F_2) / (A_1 - A_2)
            y = ((F_1 * A_2) - (F_2 * A_1)) / (A_2 - A_1)
            F = (self.age() * x) + y
            value = value * F
        '''

        if self.age() is not None and not isinstance(self.age(),str):
            if self.age() <= 20:
                value = value * 1.10
            elif self.age() == 21:
                value = value * 1.08
            elif self.age() == 22:
                value = value * 1.05
            elif self.age() < 25:
                value = value * 1.02
            elif self.age() > 37 and 'D' not in self.position:
                value = value * 0.85

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
