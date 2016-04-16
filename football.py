'''
@author: jdasilva
'''
import unittest

from player import Player


class FootballPlayer(Player):

    def __init__(self, name=None, team=None, properties={}):
        super(FootballPlayer, self).__init__(name=name, team=team, properties=properties)
        
        self.passingSDMult = 1.6
        self.rushingSDMult = 2.4
        self.receivingSDMult = 2.0
            
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

    def valuePassing(self):
        '''
        Completions    .25    0
        Incomplete Passes    -.50    0
        Passing Yards    25 yards per point; 2 points at 300 yards; 4 points at 350 yards; 6 points at 400 yards    
        Passing Touchdowns    6    4
        Interceptions    -2    -1
        Sacks    -.5    0
        '''
        
        if not self.prop.has_key("passingYards"):
            return 0
        
        points = 0.0
        points += float(self.prop['passingCompletions']) * 0.25
        points += (float(self.prop['passingAttempts']) - float(self.prop['passingCompletions'])) * -0.5 
        
        passing_yards_avg = float(self.prop['passingYards'])/17
        passing_yards_low = passing_yards_avg / self.passingSDMult
        passing_yards_high = passing_yards_avg * self.passingSDMult              
        points += (self.__valuePassingYards(passing_yards_low)*17)/2
        points += (self.__valuePassingYards(passing_yards_high)*17)/2
        
        points += float(self.prop['passingTDs'])*6
        
        points += float(self.prop['passingInterceptions'])*(-2)
        
        # 1 in 4 interceptions are pick 6
        points += float(self.prop['passingInterceptions'])/4*(-6)

        return points/17
    
    def valueRushing(self):
        '''
        Rushing Attempts    .1    0
        Rushing Yards    10 yards per point; 2 points at 100 yards; 4 points at 150 yards; 6 points at 200 yards    
        Rushing Touchdowns    6    
        '''
        
        if not self.prop.has_key("rushingYards"):
            return 0
        
        points = 0.0

        points +=  float(self.prop['rushingAttempts'])*(0.1)
        
        rushing_yards_avg = float(self.prop['rushingYards'])/17
        rushing_yards_low = rushing_yards_avg / self.rushingSDMult
        rushing_yards_high = rushing_yards_avg * self.rushingSDMult      
        points += (self.__valueRushingYards(rushing_yards_low)*17)/2
        points += (self.__valueRushingYards(rushing_yards_high)*17)/2

        points += float(self.prop['rushingTDs'])*6
                
        return points/17
    
    def valueReceiveing(self):
        '''
        Receptions    1    0
        Reception Yards    10 yards per point; 2 points at 100 yards; 4 points at 150 yards; 6 points at 200 yards    
        Reception Touchdowns    6    
        '''
        
        if not self.prop.has_key("receivingYards"):
            return 0
        
        points = 0.0
        
        points += float(self.prop['receptions'])

        receiving_yards_avg = float(self.prop['receivingYards'])/17
        receiving_yards_low = receiving_yards_avg / self.receivingSDMult
        receiving_yards_high = receiving_yards_avg * self.receivingSDMult
        points += (self.__valueReceivingYards(receiving_yards_low)*17)/2
        points += (self.__valueReceivingYards(receiving_yards_high)*17)/2

        points += float(self.prop['receivingTDs'])*6
                
        return points/17

    def valueMisc(self):
        
        points = 0.0
        
        if self.prop.has_key("fumblesLost"):
            points += (float(self.prop["fumblesLost"]) * -2)
            
        return points/17
    
    def value(self):
        
        if self.prop.has_key("hpprAvgRank"):
            return 300-(float(self.prop["hpprAvgRank"]))
        elif self.prop.has_key("avgRank"):
            return 50-(float(self.prop["avgRank"]))
        else:
            return 0
        
        #return self.valuePassing() + self.valueRushing() + self.valueReceiveing() + self.valueMisc()


if __name__ == '__main__':
    unittest.main()
