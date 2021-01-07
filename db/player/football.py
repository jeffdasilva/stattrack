import datetime
import unittest

from db.player.player import Player
from sitescraper.multisport.rotoworlddotcom import RotoWorldDotComScraper
from sitescraper.nfl.footballdbdotcom import FootballDBDotComScraper


class FootballPlayer(Player):

    DefaultRules = None

    def __init__(self, name=None, team=None, properties={}):
        super(FootballPlayer, self).__init__(name=name, team=team, properties=properties)

    def team_abbreviate(self,teamname):
        if teamname == "JAC":
            return "JAX"
        return super(FootballPlayer,self).team_abbreviate(teamname)

    def get_rules(self):
        return FootballPlayer.DefaultRules


    def toInt(self, val):
        try:
            ret_val = int(val)
        except ValueError:
            return 0
        return ret_val

###################################################################
#
# PASSING STATS
#
    def passingAttempts(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedPassingAttempts()
        else:
            return int(self.getStat(FootballDBDotComScraper.PassingAttempts, year))

    def projectedPassingAttempts(self):
        if self.getProperty('passingAttempts') is None:
            return 0.0
        else:
            return float(self.getProperty('passingAttempts'))

    def passingCompletions(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedPassingCompletions()
        else:
            return self.toInt(self.getStat(FootballDBDotComScraper.PassingCompletions, year))

    def projectedPassingCompletions(self):
        if self.getProperty('passingCompletions') is None:
            return 0.0
        else:
            return float(self.getProperty('passingCompletions'))

    def passingYards(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedPassingYards()
        else:
            return float(self.getStat(FootballDBDotComScraper.PassingYards, year))

    def projectedPassingYards(self):
        if self.getProperty('passingYards') is None:
            return 0.0
        else:
            return float(self.getProperty('passingYards'))

    def passingTDs(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedPassingTDs()
        else:
            return self.toInt(self.getStat(FootballDBDotComScraper.PassingTDs, year))

    def projectedPassingTDs(self):
        if self.getProperty('passingTDs') is None:
            return 0.0
        else:
            return float(self.getProperty('passingTDs'))

    def passingInterceptionsThrown(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedPassingInterceptionsThrown()
        else:
            return float(self.getStat(FootballDBDotComScraper.PassingInterceptionsThrown, year))

    def projectedPassingInterceptionsThrown(self):
        if self.getProperty('passingInterceptions') is None:
            return 0.0
        else:
            return float(self.getProperty('passingInterceptions'))

    def passingTwoPointers(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedPassingTwoPointers()
        else:
            return float(self.getStat(FootballDBDotComScraper.PassingTwoPointers, year))

    def projectedPassingTwoPointers(self):
        return self.passingTwoPointers(year=(datetime.datetime.now().year-1))

###################################################################
#
# RUSHING STATS
#
    def rushingAttempts(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedRushingAttempts()
        else:
            return float(self.getStat(FootballDBDotComScraper.RushingAttempts, year))

    def projectedRushingAttempts(self):
        if self.getProperty('rushingAttempts') is None:
            return 0.0
        else:
            return float(self.getProperty('rushingAttempts'))

    def rushingYards(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedRushingYards()
        else:
            return float(self.getStat(FootballDBDotComScraper.RushingYards, year))

    def projectedRushingYards(self):
        if self.getProperty('rushingYards') is None:
            return 0.0
        else:
            return float(self.getProperty('rushingYards'))

    def rushingTDs(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedRushingTDs()
        else:
            return self.toInt(self.getStat(FootballDBDotComScraper.RushingTDs, year))

    def projectedRushingTDs(self):
        if self.getProperty('rushingTDs') is None:
            return 0.0
        else:
            return float(self.getProperty('rushingTDs'))

    def rushingTwoPointers(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedRushingTwoPointers()
        else:
            return self.toInt(self.getStat(FootballDBDotComScraper.ReceivingTwoPointers, year))

    def projectedRushingTwoPointers(self):
        return self.rushingTwoPointers(year=(datetime.datetime.now().year-1))


###################################################################
#
# RECEIVING STATS
#
    def receptions(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedReceptions()
        else:
            return self.toInt(self.getStat(FootballDBDotComScraper.Receptions, year))

    def projectedReceptions(self):
        if self.getProperty('receptions') is None:
            return 0.0
        else:
            return float(self.getProperty('receptions'))

    def receivingYards(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedReceivingYards()
        else:
            return float(self.getStat(FootballDBDotComScraper.ReceivingYards, year))

    def projectedReceivingYards(self):
        if self.getProperty('receivingYards') is None:
            return 0.0
        else:
            return float(self.getProperty('receivingYards'))

    def receivingTDs(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedReceivingTDs()
        else:
            return self.toInt(self.getStat(FootballDBDotComScraper.ReceivingTDs, year))

    def projectedReceivingTDs(self):
        if self.getProperty('receivingTDs') is None:
            return 0.0
        else:
            return float(self.getProperty('receivingTDs'))

    def receivingTwoPointers(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedReceivingTwoPointers()
        else:
            return self.toInt(self.getStat(FootballDBDotComScraper.ReceivingTwoPointers, year))

    def projectedReceivingTwoPointers(self):
        return self.receivingTwoPointers(year=(datetime.datetime.now().year-1))


###################################################################
#
# MISC STATS
#
    def fumblesLost(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedFumblesLost()
        else:
            return self.toInt(self.getStat(FootballDBDotComScraper.FumblesLost, year))

    def projectedFumblesLost(self):
        if self.getProperty('fumblesLost') is None:
            return 0.0
        else:
            return float(self.getProperty('fumblesLost'))

    def fumbleTDs(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedFumbleTDs()
        else:
            return self.toInt(self.getStat(FootballDBDotComScraper.FumbleTDs, year))

    def projectedFumbleTDs(self):
        return self.fumbleTDs(year=(datetime.datetime.now().year-1))

    def gamesPlayed(self,year=datetime.datetime.now().year):
        if year == datetime.datetime.now().year:
            return self.projectedGamesPlayed()
        else:
            return self.toInt(self.getStat(RotoWorldDotComScraper.GamesPlayed, year))

    def projectedGamesPlayed(self):
        return 17

###################################################################



    def points(self,year=datetime.datetime.now().year):

        if self.get_rules() is not None:
            return self.get_rules().points(self, year)

        raise ValueError('Should not reach here')
        return 0.0

    def pointsPerGame(self,year=datetime.datetime.now().year):
        if self.gamesPlayed(year) == 0:
            return 0.0
        else:
            return self.points(year)/self.gamesPlayed(year)


    # deprecated
    def __valuePassingYards(self,passingYards):
        points = 0.0

        if passingYards > 400:
            points += ((passingYards-400)/25) * 6
            passingYards = 400

        if passingYards > 350:
            points += ((passingYards-350)/25) * 4
            passingYards = 350

        if passingYards > 300:
            points += ((passingYards-300)/25) * 2
            passingYards = 300

        points += passingYards/25

        return points

    # deprecated
    def __valueRushingYards(self,rushingYards):
        points = 0.0

        if rushingYards > 200:
            points += ((rushingYards-200)/10) * 6
            rushingYards = 200

        if rushingYards > 150:
            points += ((rushingYards-150)/10) * 4
            rushingYards = 150

        if rushingYards > 100:
            points += ((rushingYards-100)/10) * 2
            rushingYards = 100

        points += rushingYards/10

        return points

    # deprecated
    def __valueReceivingYards(self,receivingYards):
        points = 0.0

        if receivingYards > 200:
            points += ((receivingYards-200)/10) * 6
            receivingYards = 200

        if receivingYards > 150:
            points += ((receivingYards-150)/10) * 4
            receivingYards = 150

        if receivingYards > 100:
            points += ((receivingYards-100)/10) * 2
            receivingYards = 100

        points += receivingYards/10

        return points

    # deprecated
    def valuePassing(self):
        '''
        Completions    .25    0
        Incomplete Passes    -.50    0
        Passing Yards    25 yards per point; 2 points at 300 yards; 4 points at 350 yards; 6 points at 400 yards
        Passing Touchdowns    6    4
        Interceptions    -2    -1
        Sacks    -.5    0
        '''

        if not self.property.has_key("passingYards"):
            return 0

        points = 0.0
        points += float(self.getProperty('passingCompletions')) * 0.25
        points += (float(self.getProperty('passingAttempts')) - float(self.getProperty('passingCompletions'))) * -0.5

        passing_yards_avg = float(self.getProperty('passingYards'))/17
        passing_yards_low = passing_yards_avg / self.passingSDMult
        passing_yards_high = passing_yards_avg * self.passingSDMult
        points += (self.__valuePassingYards(passing_yards_low)*17)/2
        points += (self.__valuePassingYards(passing_yards_high)*17)/2

        points += float(self.getProperty('passingTDs'))*6

        points += float(self.getProperty('passingInterceptions'))*(-2)

        # 1 in 4 interceptions are pick 6
        points += float(self.getProperty('passingInterceptions'))/4*(-6)

        return points/17

    # deprecated
    def valueRushing(self):
        '''
        Rushing Attempts    .1    0
        Rushing Yards    10 yards per point; 2 points at 100 yards; 4 points at 150 yards; 6 points at 200 yards
        Rushing Touchdowns    6
        '''

        if not self.property.has_key("rushingYards"):
            return 0

        points = 0.0

        points +=  float(self.getProperty('rushingAttempts'))*(0.1)

        rushing_yards_avg = float(self.getProperty('rushingYards'))/17
        rushing_yards_low = rushing_yards_avg / self.rushingSDMult
        rushing_yards_high = rushing_yards_avg * self.rushingSDMult
        points += (self.__valueRushingYards(rushing_yards_low)*17)/2
        points += (self.__valueRushingYards(rushing_yards_high)*17)/2

        points += float(self.getProperty('rushingTDs'))*6

        return points/17

    # deprecated
    def valueReceiveing(self):
        '''
        Receptions    1    0
        Reception Yards    10 yards per point; 2 points at 100 yards; 4 points at 150 yards; 6 points at 200 yards
        Reception Touchdowns    6
        '''

        if not self.property.has_key("receivingYards"):
            return 0

        points = 0.0

        points += float(self.property['receptions'])

        receiving_yards_avg = float(self.getProperty('receivingYards'))/17
        receiving_yards_low = receiving_yards_avg / self.receivingSDMult
        receiving_yards_high = receiving_yards_avg * self.receivingSDMult
        points += (self.__valueReceivingYards(receiving_yards_low)*17)/2
        points += (self.__valueReceivingYards(receiving_yards_high)*17)/2

        points += float(self.getProperty('receivingTDs'))*6

        return points/17

    # deprecated
    def valueMisc(self):

        points = 0.0

        if self.property.has_key("fumblesLost"):
            points += (float(self.getProperty("fumblesLost")) * -2)

        return points/17


    # ToDo: Make this better!!!
    def value(self):

        if 'K' in self.position or 'DEF' in self.position:
            return (500.0 - float(self.property.get("pprRank", 500.0)))/40.0

        '''
        if datetime.datetime.now().month  < 6:
            try:
                if self.property.has_key("hpprAvgRank"):
                    return 300-(float(self.property["hpprAvgRank"]))
                elif self.property.has_key("avgRank"):
                    return 50-(float(self.property["avgRank"]))
                else:
                    return 0
            except ValueError:
                return 0
        '''
        #...and if we're in July, we have projections
        #return self.valuePassing() + self.valueRushing() + self.valueReceiveing() + self.valueMisc()
        return self.pointsPerGame()


class TestFootballPlayer(unittest.TestCase):

    def testNewFootballPlayer(self):
        fp = FootballPlayer(name="Jeff", team="SF", properties={"position":"WR","foo":"bar","name":"DaSilva"})

        self.assertEquals(fp.name,"DaSilva")
        self.assertEquals(fp.team,"SF")
        self.assertEquals(fp.position,["WR"])
        self.assertEquals(fp.property["foo"],"bar")


if __name__ == '__main__':
    unittest.main()
