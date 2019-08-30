#!/usr/bin/env python

import datetime
import unittest

from sitescraper.scraper import SiteScraper


class FantasyProsDotComScraper(SiteScraper):

    def __init__(self):
        super(FantasyProsDotComScraper, self).__init__(url="https://www.fantasypros.com/nfl")
        #self.maxCacheTime = datetime.timedelta(days=7)
        #self.maxCacheTime = datetime.timedelta(hours=1)
        self.maxCacheTime = datetime.timedelta(days=1)
        #self.maxCacheTime = datetime.timedelta()
        
        self.setProjectionURLs()
        self.setCheatSheetURLs()
        self.debug = True

    def setProjectionURLs(self, week="draft"):
        url_offset = "/projections/"
        url_suffix = ".php?week=" + week

        self.projectionsURL = {}
        for p in ['QB', 'RB', 'WR', 'TE', 'K']:
            self.projectionsURL[p] = url_offset + p.lower() + url_suffix

        self.setProjectionKeys()

    def setProjectionKeys(self):
        keysPositionNameTeam = ['position', 'name', 'team']
        keysPassingStats = ['passingAttempts', 'passingCompletions', 'passingYards', 'passingTDs', 'passingInterceptions']
        keysRushingStats = ['rushingAttempts', 'rushingYards', 'rushingTDs' ]
        keysReceivingStats = ['receptions', 'receivingYards', 'receivingTDs' ]
        keysMiscStats =  [ 'fumblesLost', 'fantasyPoints' ]

        self.keys = {}
        self.keys['QB'] = keysPositionNameTeam + keysPassingStats + keysRushingStats + keysMiscStats
        self.keys['RB'] = keysPositionNameTeam + keysRushingStats + keysReceivingStats + keysMiscStats
        self.keys['WR'] = keysPositionNameTeam + keysReceivingStats + keysRushingStats + keysMiscStats
        self.keys['TE'] = keysPositionNameTeam + keysReceivingStats + keysMiscStats
        self.keys['K'] = keysPositionNameTeam + ['fieldGoals', 'fieldGoalAttempts', 'extraPoints', 'fantasyPoints']

    def setCheatSheetURLs(self):
        url_offset = "/rankings/"
        url_suffix = "-cheatsheets.php"

        self.cheatsheetURL = {}
        for p in [ 'QB', 'RB', 'WR', 'TE', 'K', 'dst', 'consensus', 'ppr', 'half-point-ppr' ]:
            self.cheatsheetURL[p] = url_offset + p.lower() + url_suffix

    def scrapeCheatSheets(self):

        self.cheatsheets = []

        for p in self.cheatsheetURL:
            data = self.scrapeTable(urlOffset=self.cheatsheetURL[p], attrs={'id': 'rank-data'})

            if data is None:
                print("ERROR: table for " + p + " from " + self.cheatsheetURL[p] + " could not be extracted")
                continue

            if p == "dst":
                pos = "DEF"
            else:
                pos = p;

            if p == "consensus":
                dataKeys = ['stdRank', 'name', 'team', 'stdPositionAndRank', 'byeWeek', 'stdBestRank', 'stdWorstRank', 'stdAvgRank', 'stdStdDev']
            elif p == "ppr":
                dataKeys = ['pprRank', 'name', 'team', 'pprPositionAndRank', 'byeWeek', 'pprBestRank', 'pprWorstRank', 'pprAvgRank', 'pprStdDev']
            elif p == "half-point-ppr":
                dataKeys = ['hpprRank', 'name', 'team', 'hpprPositionAndRank', 'byeWeek', 'hpprBestRank', 'hpprWorstRank', 'hpprAvgRank', 'hpprStdDev']
            else:
                dataKeys = ['position', 'positionRank', 'name', 'team', 'byeWeek', 'bestRank', 'worstRank', 'avgRank', 'stdDev']

            for data_i in data:
                if len(data_i) < 3: continue
                #print(data_i)
                
                # remove wsid field
                data_i = [data_i[0]] + data_i[2:]

                #print str(data_i) + " " + str(len(data_i))
                if p == "half-point-ppr" or p == "ppr" or p == "consensus":
                    d = dict(zip(dataKeys,[data_i[0]] + self.splitNameTeamString(data_i[1]) + data_i[2:]))
                else:
                    d = dict(zip(dataKeys,[pos] + [data_i[0]] + self.splitNameTeamString(data_i[1]) + data_i[2:]))

                d['name'] = d['name'].rstrip()
                
                if d['name'] in ['&nbsp', 'Team']: continue
                if '(Team)' in d['name']: continue
                
                #print('NAME:' + d['name'] + " POS:" + pos)

                self.cheatsheets.append(d)

    def scrapeProjections(self):

        self.projections = []

        for p in self.projectionsURL:
            #s = SiteScraper(self.projectionsURL[p])
            data = self.scrapeTable(urlOffset=self.projectionsURL[p], attrs={'id': 'data'})

            if data is None:
                continue

            if p == 'K':
                data = data[1:]
            else:
                data = data[2:]

            for data_i in data:
                d = dict(zip(self.keys[p],[p] + self.splitNameTeamString(data_i[0]) + data_i[1:]))
                if d['name'].startswith('  '):
                    raise ValueError("Space char found at the beginning of name: " + d['name'] + " --- " + data_i)
                self.projections.append(d)

    def scrape(self):
        self.cheatsheets = []
        self.projections = []
        self.scrapeProjections()
        self.scrapeCheatSheets()
        data = self.cheatsheets + self.projections
        return data

    def splitNameTeamString(self, nameTeamStr):

        if nameTeamStr.endswith(' DST'):
            nameTeamStr = nameTeamStr[:-4]
            if '(' in nameTeamStr and ')' in nameTeamStr:
                name,team = nameTeamStr.rsplit('(',1)
                team = team.split(')',1)[0]
                return [name.strip(), team.strip()]


        if len(nameTeamStr) > 6 and nameTeamStr.rfind(nameTeamStr[0] + '.') != -1:
            idx = nameTeamStr.rfind(nameTeamStr[0] + '.')
            if idx != 0:
                nameTeamStr = nameTeamStr[0:idx] + ' ' +  nameTeamStr[-3:]

        if len(nameTeamStr.rsplit(' ',1)) > 1 and \
            len(nameTeamStr.rsplit(' ',1)[1]) == 1:
            nameTeamStr = nameTeamStr.rsplit(' ',1)[0]

        if len(str(nameTeamStr).split()) < 3 or \
            not str(nameTeamStr).rsplit(' ',1)[1].isupper() or \
            len(str(nameTeamStr).rsplit(' ',1)[1]) > 3:

            return [ nameTeamStr, 'unknown' ]
        else:
            return str(nameTeamStr).rsplit(' ',1)


class TestFantasyProsDotComScraper(unittest.TestCase):

    def testFantasyProsScraper(self):

        s = FantasyProsDotComScraper();
        s.scrape()

        camNewtonFound = False
        tomBradyFound = False
        for player in s.projections:
            #print player
            if player['name'] == "Cam Newton":
                print player
                self.assertGreater(player['passingYards'], 2000)
                self.assertGreater(player['rushingYards'], 200)
                self.assertEqual(player['team'], "CAR")
                self.assertEqual(player['position'], "QB")
                self.assertEquals(camNewtonFound,False)
                camNewtonFound = True

            if player['name'] == "Tom Brady":
                print player
                tomBradyFound = True

        current_month = datetime.datetime.now().month

        if current_month > 6:
            # this will not work in April/May
            self.assertEquals(camNewtonFound,True)
            self.assertEquals(tomBradyFound,True)

        seattleFound = 0
        for player in s.cheatsheets:
            if player['name'] == "Seattle":
                if 'position' in player:
                    self.assertEqual(player['position'], "DEF")
                seattleFound += 1

        self.assertEquals(seattleFound,4)

    def testsplitNameTeamString(self):
        s = FantasyProsDotComScraper();
        self.assertEquals(s.splitNameTeamString("foo")[1],"unknown")
        self.assertEquals(s.splitNameTeamString("foo")[0],"foo")
        self.assertEquals(s.splitNameTeamString("foo bar")[1],"unknown")
        self.assertEquals(s.splitNameTeamString("foo bar foobar")[1],"unknown")
        self.assertEquals(s.splitNameTeamString("foo bar foo")[1],"unknown")
        self.assertEquals(s.splitNameTeamString("foo bar FOO")[1],"FOO")
        self.assertEquals(s.splitNameTeamString("foo bar FO")[1],"FO")
        self.assertEquals(s.splitNameTeamString("foo bar FOOO")[1],"unknown")
        self.assertEquals(s.splitNameTeamString("foo bar FOOO")[0],"foo bar FOOO")

if __name__ == '__main__':
    unittest.main()