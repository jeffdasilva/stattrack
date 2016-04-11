'''
@author: jdasilva
'''
from bs4 import BeautifulSoup
import unittest
import urllib

from player import Player
from playerdb import PlayerDB


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
        
        if not self.prop.has_key("fumblesLost"):
            points += (float(self.prop("fumblesLost")) * -2)
            
        return points/17
    
    def value(self):
        return self.valuePassing() + self.valueRushing() + self.valueReceiveing()


class FootballPlayerDB(PlayerDB):

    def __init__(self):
        
        pmap = {}
        pmap["qb"] = [ "QB" ]
        pmap["quarterback"] = [ "QB" ]
        pmap["rb"] = [ "RB" ]
        pmap["runningback"] = [ "RB" ]
        pmap["wr"] = [ "WR", "TE" ]
        pmap["widereceiver"] = [ "WR", "TE" ]
        pmap["te"] = [ "TE" ]
        pmap["tightend"] = [ "TE" ]
        #pmap["k"] = [ "K" ]
        #pmap["kicker"] = [ "K" ]
        
        super(FootballPlayerDB, self).__init__(positionMap=pmap)
        
        self.numberOfTeams = 10
        self.numberOfStarting = {}
        self.numberOfStarting['qb'] = 2
        self.numberOfStarting['rb'] = 3
        self.numberOfStarting['wr'] = 4
        self.numberOfScrubs = 14 - self.numberOfStarting['qb'] - self.numberOfStarting['rb'] - self.numberOfStarting['wr']
        self.moneyPerTeam = 333
        
    def wget(self):
        self.wgetFantasyPros()

    def wgetFantasyPros(self):

        site_root = "http://www1.fantasypros.com/nfl"
        site = {}
        site_suffix = "?week=draft"

        site['QB'] = site_root + "/projections/qb.php" + site_suffix
        site['RB'] = site_root + "/projections/rb.php" + site_suffix
        site['WR'] = site_root + "/projections/wr.php" + site_suffix
        site['TE'] = site_root + "/projections/te.php" + site_suffix
        site['K'] = site_root + "/projections/k.php" + site_suffix

        for position in ['QB', 'RB', 'WR', 'TE']:

            f = urllib.urlopen(site[position])
            html = f.read()
            soup = BeautifulSoup(html)
            table = soup.find('table', {'id': 'data'})

            rawdata = []

            for row in table.findAll("tr"):
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                rawdata.append([ele for ele in cols if ele]) 

            if position == 'K':
                rawdata = rawdata[1:]
            else:
                rawdata = rawdata[2:]

            stats = []
            for i in rawdata:
                if len(str(i[0]).split()) < 3 or not str(i[0]).rsplit(' ',1)[1].isupper() or str(i[0]).rsplit(' ',1)[1].isupper() > 3:                 
                    stats += [ [ i[0] ] + [ 'unknown' ] + [ position ] + i[1:] ]                
                else: 
                    stats += [ str(i[0]).rsplit(' ',1) + [ position ] + i[1:] ]

            #print stats

            statDesc = ['name', 'team', 'position']

            if position == 'K':
                statDesc += ['fieldGoals', 'fieldGoalAttempts', 'extraPoints']
            else:
                if position == 'QB':
                    statDesc += ['passingAttempts', 'passingCompletions', 'passingYards', 'passingTDs', 'passingInterceptions']

                if position != 'TE':
                    statDesc += ['rushingAttempts', 'rushingYards', 'rushingTDs' ]

                if position != 'QB':
                    statDesc += ['receptions', 'receivingYards', 'receivingTDs' ]

                statDesc += ['fumblesLost' ]
            
            statDesc += [ 'fantasyPoints' ]

            for player_stats in stats:
                player_prop = {}
                index = 0
                for stat in statDesc:
                    player_prop[stat] = player_stats[index].replace(',', '')
                    index += 1 
                
                player = FootballPlayer(properties=player_prop)
                self.add(player)
        
    def moneyRemaining(self):
        total_money = self.numberOfTeams * self.moneyPerTeam
        
        for p in self.player.itervalues():
            if p.isDrafted:
                total_money -= p.cost
        
        return total_money
    
    def remainingGoodPlayersByPosition(self, position):
        num_players_remaining = self.numberOfStarting[position]*self.numberOfTeams - self.numberOfPlayersDrafted(position=position)
        return self.get(position=position)[:num_players_remaining]
    
    def remainingGoodPlayers(self):
        return max(self.remainingGoodPlayersByPosition(position="wr"),3) \
            + max(self.remainingGoodPlayersByPosition(position="qb"),3) \
            + max(self.remainingGoodPlayersByPosition(position="rb"),3)
    
    def valueRemaining(self):
        value = 0
        for p in self.remainingGoodPlayers():
            value += p.value()
        return value
    
    def costPerValueUnit(self):
        return self.moneyRemaining() / max(self.valueRemaining(),0.1) 
        

class TestFootballPlayer(unittest.TestCase):

    def testNewFootballPlayer(self):
        fp = FootballPlayer(name="Jeff", team="SF", properties={"position":"WR","foo":"bar","name":"DaSilva"})

        self.assertEquals(fp.name,"DaSilva")
        self.assertEquals(fp.team,"SF")
        self.assertEquals(fp.position,["WR"])
        self.assertEquals(fp.prop["foo"],"bar")


class TestFootballPlayerDB(unittest.TestCase):

    def testNewFootballPlayerDB(self):
        fdb = FootballPlayerDB()
        self.assertTrue(len(fdb.positionMap.keys()) > 5)
        #self.assertEquals(fdb.positionMap["kicker"],["K"]) 
        pass
    
    def testRemainingPlayer(self):
        fdb = FootballPlayerDB()
        fdb.load()
        
        cpv_mult = fdb.costPerValueUnit()
        
        for p in fdb.remainingGoodPlayers():
            print str(p) + " $" + str(cpv_mult * p.value())
            
        print fdb.valueRemaining(), fdb.moneyRemaining(), fdb.costPerValueUnit()
        

    def testMoneyRemaining(self):
        fdb = FootballPlayerDB()
        fdb.add(Player("June"))
        fdb.add(Player("Sophia"))        
        self.assertEqual(fdb.moneyRemaining(),3330)
        
        fdb.get("June")[0].draft(10)
        self.assertEqual(fdb.moneyRemaining(),3320)

        fdb.get("Sophia")[0].draft(111)
        self.assertEqual(fdb.moneyRemaining(),3209)

        

    def testWget(self):
        fdb = FootballPlayerDB()
        fdb.wget()

        p = fdb.player["Tom Brady - NE"]
        print p
        self.assertEquals(p.position,["QB"])
        self.assertTrue(float(p.prop["fantasyPoints"]) > 200)
        self.assertTrue(float(p.prop["passingAttempts"]) > 500)
        self.assertTrue(float(p.prop["passingYards"]) > 3000)

        print p.value()

        p = fdb.player["Rob Gronkowski - NE"]
        self.assertEquals(p.position,["TE"])
        self.assertTrue(p.prop["fantasyPoints"] > 100) 
        self.assertTrue(p.prop["receivingYards"] > 400)

        #p = fdb.player["Garrett Hartley - PIT"]
        #self.assertEquals(p.position,["K"])
        #self.assertTrue(p.prop["fantasyPoints"] > 100) 
        #self.assertTrue(p.prop["extraPoints"] > 10) 

        p = fdb.player["Calvin Johnson - unknown"]
        self.assertEquals(p.position,["WR"])
        self.assertTrue(p.prop["fantasyPoints"] > 180) 
        self.assertTrue(p.prop["receivingYards"] > 400)

        pass

    def testValAndSort(self):
        fdb = FootballPlayerDB()
        fdb.add(FootballPlayer("Jeff DS","SF",{"fantasyPoints":"24"}))
        fdb.add(FootballPlayer("Jeff","SF",{"fantasyPoints":"124"}))
        fdb.add(FootballPlayer("Jeffx","SF",{"fantasyPoints":"14"}))
        #self.assertEquals(fdb.get("Jeff")[0].prop['fantasyPoints'],124)

if __name__ == '__main__':
    unittest.main()
