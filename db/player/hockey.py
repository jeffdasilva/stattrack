import datetime
import unittest

from db.player.player import Player


class HockeyPlayer(Player):

    def __init__(self, name=None, team=None, properties={}):
        super(HockeyPlayer, self).__init__(name=name, team=team, properties=properties)


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
            #return int(self.getStat(HockeyDBDotComScraper.Goals, year))
            return 0

    def projectedGoals(self):
        return float(self.getProperty('tsn.top300.goals',0))

    def assists(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedAssists()
        else:
            #return int(self.getStat(HockeyDBDotComScraper.Assists, year))
            return 0

    def projectedAssists(self):
        return float(self.getProperty('tsn.top300.assists',0))

    def goaltenderWins(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedGoaltenderWins()
        else:
            #return int(self.getStat(HockeyDBDotComScraper.Wins, year))
            return 0

    def projectedGoaltenderWins(self):
        return float(self.getProperty('tsn.by_pos.wins',0))

    def goaltenderTies(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedGoaltenderTies()
        else:
            #return int(self.getStat(HockeyDBDotComScraper.Ties, year))
            return 0

    def projectedGoaltenderTies(self):
        return float(self.getProperty('tsn.by_pos.ties',0))


    def goaltenderShutOuts(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedGoaltenderShutOuts()
        else:
            #return int(self.getStat(HockeyDBDotComScraper.ShutOuts, year))
            return 0

    def projectedGoaltenderShutOuts(self):
        return float(self.getProperty('tsn.by_pos.shutouts',0))

    def gamesPlayed(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedGamesPlayed()
        else:
            #return int(self.getStat(HockeyDBDotComScraper.Games, year))
            return 0

    def projectedGamesPlayed(self):
        if self.getProperty('tsn.by_pos.games') is None:
            return 0.0
        else:
            return float(self.getProperty('tsn.by_pos.games'))

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

    def testTeamAbbreviate(self):
        p = HockeyPlayer(name="noname")
        self.assertEqual(p.team_abbreviate('Pittsburgh'),'pit')
        self.assertEqual(p.team_abbreviate('.P.I.T.'),'pit')


if __name__ == '__main__':
    unittest.main()
