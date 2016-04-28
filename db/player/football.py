'''
@author: jdasilva
'''

import datetime
import unittest

from db.player.player import Player
from sitescraper.multisport.rotoworlddotcom import RotoWorldDotComScraper
from sitescraper.nfl.footballdbdotcom import FootballDBDotComScraper


class FootballPlayer(Player):

    def __init__(self, name=None, team=None, properties={}):
        super(FootballPlayer, self).__init__(name=name, team=team, properties=properties)

        self.passingSDMult = 1.6
        self.rushingSDMult = 2.4
        self.receivingSDMult = 2.0


    def getStat(self, statName, year=datetime.datetime.now().year):
        if str(year) in self.property:
            if statName in self.property[str(year)]:
                stat = self.property[str(year)][statName].replace(',','')
                return stat
        return 0;

    def passingAttempts(self,year=datetime.datetime.now().year):
        return int(self.getStat(FootballDBDotComScraper.PassingAttempts, year))

    def passingCompletions(self,year=datetime.datetime.now().year):
        return int(self.getStat(FootballDBDotComScraper.PassingCompletions, year))

    def passingYards(self,year=datetime.datetime.now().year):
        return float(self.getStat(FootballDBDotComScraper.PassingYards, year))

    def passingTDs(self,year=datetime.datetime.now().year):
        return int(self.getStat(FootballDBDotComScraper.PassingTDs, year))

    def passingInterceptionsThrown(self,year=datetime.datetime.now().year):
        return int(self.getStat(FootballDBDotComScraper.PassingInterceptionsThrown, year))

    def passingTwoPointers(self,year=datetime.datetime.now().year):
        return int(self.getStat(FootballDBDotComScraper.PassingTwoPointers, year))

    def rushingAttempts(self,year=datetime.datetime.now().year):
        return int(self.getStat(FootballDBDotComScraper.RushingAttempts, year))

    def rushingYards(self,year=datetime.datetime.now().year):
        return float(self.getStat(FootballDBDotComScraper.RushingYards, year))

    def rushingTDs(self,year=datetime.datetime.now().year):
        return int(self.getStat(FootballDBDotComScraper.RushingTDs, year))

    def rushingTwoPointers(self,year=datetime.datetime.now().year):
        return int(self.getStat(FootballDBDotComScraper.ReceivingTwoPointers, year))

    def receptions(self,year=datetime.datetime.now().year):
        return int(self.getStat(FootballDBDotComScraper.Receptions, year))

    def receivingYards(self,year=datetime.datetime.now().year):
        return float(self.getStat(FootballDBDotComScraper.ReceivingYards, year))

    def receivingTDs(self,year=datetime.datetime.now().year):
        return int(self.getStat(FootballDBDotComScraper.ReceivingTDs, year))

    def receivingTwoPointers(self,year=datetime.datetime.now().year):
        return int(self.getStat(FootballDBDotComScraper.ReceivingTwoPointers, year))

    def fumblesLost(self,year=datetime.datetime.now().year):
        return int(self.getStat(FootballDBDotComScraper.FumblesLost, year))

    def fumbleTDs(self,year=datetime.datetime.now().year):
        return int(self.getStat(FootballDBDotComScraper.FumbleTDs, year))

    def gamesPlayed(self,year=datetime.datetime.now().year):
        return int(self.getStat(RotoWorldDotComScraper.GamesPlayed, year))

    def age(self,year=datetime.datetime.now().year):
        if 'rotoworld' in self.property:
            age = str(self.property['rotoworld'][1][1]).split(' / ')[0].lstrip('(').rstrip(')')
            return int(age)
        else:
            return 0

    def points(self,year=datetime.datetime.now().year):

        points = 0.0
        points += self.passingTDs(year) * (4)
        points += self.passingYards(year) * (0.04)
        points += self.passingInterceptionsThrown(year) * (-1)
        points += self.passingTwoPointers(year) * (2)
        points += self.rushingTDs(year) * (6)
        points += self.rushingYards(year) * (0.1)
        points += self.rushingTwoPointers(year) * (2)
        points += self.receivingTDs(year) * (6)
        points += self.receivingYards(year) * (0.1)
        points += self.receptions(year) * (0.5)
        points += self.receivingTwoPointers(year) * (2)
        # fieldgoal stats needed
        # punt return TDs * 6
        # kick return TDs * 6
        points += self.fumblesLost(year) * (-2)
        points += self.fumbleTDs(year) * (6)

        return points

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
        points += float(self.property['passingCompletions']) * 0.25
        points += (float(self.property['passingAttempts']) - float(self.property['passingCompletions'])) * -0.5

        passing_yards_avg = float(self.property['passingYards'])/17
        passing_yards_low = passing_yards_avg / self.passingSDMult
        passing_yards_high = passing_yards_avg * self.passingSDMult
        points += (self.__valuePassingYards(passing_yards_low)*17)/2
        points += (self.__valuePassingYards(passing_yards_high)*17)/2

        points += float(self.property['passingTDs'])*6

        points += float(self.property['passingInterceptions'])*(-2)

        # 1 in 4 interceptions are pick 6
        points += float(self.property['passingInterceptions'])/4*(-6)

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

        points +=  float(self.property['rushingAttempts'])*(0.1)

        rushing_yards_avg = float(self.property['rushingYards'])/17
        rushing_yards_low = rushing_yards_avg / self.rushingSDMult
        rushing_yards_high = rushing_yards_avg * self.rushingSDMult
        points += (self.__valueRushingYards(rushing_yards_low)*17)/2
        points += (self.__valueRushingYards(rushing_yards_high)*17)/2

        points += float(self.property['rushingTDs'])*6

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

        receiving_yards_avg = float(self.property['receivingYards'])/17
        receiving_yards_low = receiving_yards_avg / self.receivingSDMult
        receiving_yards_high = receiving_yards_avg * self.receivingSDMult
        points += (self.__valueReceivingYards(receiving_yards_low)*17)/2
        points += (self.__valueReceivingYards(receiving_yards_high)*17)/2

        points += float(self.property['receivingTDs'])*6

        return points/17

    # deprecated
    def valueMisc(self):

        points = 0.0

        if self.property.has_key("fumblesLost"):
            points += (float(self.property["fumblesLost"]) * -2)

        return points/17


    # ToDo: Make this better!!!
    def value(self):

        if self.property.has_key("hpprAvgRank"):
            return 300-(float(self.property["hpprAvgRank"]))
        elif self.property.has_key("avgRank"):
            return 50-(float(self.property["avgRank"]))
        else:
            return 0

        #return self.valuePassing() + self.valueRushing() + self.valueReceiveing() + self.valueMisc()


if __name__ == '__main__':
    unittest.main()
