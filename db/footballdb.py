'''
Created on April 12, 2016

@author: jdasilva
'''

from bs4 import BeautifulSoup
import unittest
import urllib

from db.player.football import FootballPlayer
from db.player.player import Player
from db.playerdb import PlayerDB


class FootballPlayerDB(PlayerDB):

    def __init__(self):

        pmap = {}
        pmap["qb"] = [ "QB" ]
        pmap["quarterback"] = [ "QB" ]
        pmap["rb"] = [ "RB" ]
        pmap["runningback"] = [ "RB" ]
        pmap["wr"] = [ "WR", "TE" ]
        pmap["widereceiver"] = [ "WR", "TE" ]
        #pmap["wr"] = [ "WR" ]
        #pmap["widereceiver"] = [ "WR" ]
        pmap["te"] = [ "TE" ]
        pmap["tightend"] = [ "TE" ]
        pmap["k"] = [ "K" ]
        pmap["kicker"] = [ "K" ]

        pmap["def"] = [ "DEF" ]
        pmap["defence"] = [ "DEF" ]
        pmap["defense"] = [ "DEF" ]


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
        self.wgetFantasyProsCheatsheets()

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

    def wgetFantasyProsCheatsheets(self):

        site_root = "http://www1.fantasypros.com/nfl/rankings"
        site = {}
        site_suffix = "-cheatsheets.php"

        site['QB'] = site_root + "/qb" + site_suffix
        site['RB'] = site_root + "/rb" + site_suffix
        site['WR'] = site_root + "/wr" + site_suffix
        site['TE'] = site_root + "/te" + site_suffix
        site['K'] = site_root + "/k" + site_suffix
        site['DEF'] = site_root + "/dst" + site_suffix
        site['ALL'] = site_root + "/half-point-ppr" + site_suffix


        for position in ['QB', 'RB', 'WR', 'TE', 'K', 'DEF', 'ALL']:

            f = urllib.urlopen(site[position])
            html = f.read()
            soup = BeautifulSoup(html)
            table = soup.find('table', {'id': 'data'})

            rawdata = []

            for row in table.findAll("tr"):
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                rawdata.append([ele for ele in cols])

            rawdata = rawdata[1:]

            stats = []
            for i in rawdata:
                if (len(i)) <= 1:
                    continue

                rank = i[0]
                i = i[1:]

                if len(str(i[0]).split()) < 3 or not str(i[0]).rsplit(' ',1)[1].isupper() or str(i[0]).rsplit(' ',1)[1].isupper() > 3:
                    stats += [ [rank] + [ i[0] ] + [ 'unknown' ] ]
                else:
                    stats += [ [rank] + str(i[0]).rsplit(' ',1)]

                if position != 'ALL':
                    stats[-1] += [position]

                stats[-1] += i[1:]

            if position == 'ALL':
                statDesc = ['hpprRank', 'name', 'team', 'positionAndRank', 'byeWeek', 'hpprBestRank', 'hpprWorstRank', 'hpprAvgRank', 'hpprStdDev']
            else:
                statDesc = ['rank', 'name', 'team', 'position', 'byeWeek', 'bestRank', 'worstRank', 'avgRank', 'stdDev']

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

    def testWgetCheatsheets(self):
        fdb = FootballPlayerDB()
        fdb.wgetFantasyProsCheatsheets()

        p = fdb.player["Julio Jones - ATL"]
        print p
        self.assertEquals(p.position,["WR"])

if __name__ == '__main__':
    unittest.main()
