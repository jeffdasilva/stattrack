
import datetime
import unittest

from sitescraper.scraper import SiteScraper


class FantasyProsDotComScraper(SiteScraper):

    def __init__(self):
        #super(FantasyProsDotComScraper, self).__init__(url="http://www1.fantasypros.com/nfl")
        super(FantasyProsDotComScraper, self).__init__(url="https://www.fantasypros.com/nfl")
        self.maxCacheTime = datetime.timedelta(days=1)
        self.setProjectionURLs()
        self.setCheatSheetURLs()
        #self.debug = True

    def setProjectionURLs(self):
        url_offset = "/projections/"
        url_suffix = ".php?week=draft"

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
        self.keys['WR'] = keysPositionNameTeam + keysRushingStats + keysReceivingStats + keysMiscStats
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
            self.scrapeTable(urlOffset=self.cheatsheetURL[p], attrs={'id': 'data'})

            if self.data is None:
                print "ERROR: table for " + p + " from " + self.cheatsheetURL[p] + " could not be extracted"
                continue

            self.data = self.data[1:]

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

            for data in self.data:
                if len(data) < 2:
                    continue
                if p == "half-point-ppr" or p == "ppr" or p == "consensus":
                    d = dict(zip(dataKeys,[data[0]] + self.splitNameTeamString(data[1]) + data[2:]))
                else:
                    d = dict(zip(dataKeys,[pos] + [data[0]] + self.splitNameTeamString(data[1]) + data[2:]))

                self.cheatsheets.append(d)

    def scrapeProjections(self):

        self.projections = []

        for p in self.projectionsURL:
            #s = SiteScraper(self.projectionsURL[p])
            self.scrapeTable(urlOffset=self.projectionsURL[p], attrs={'id': 'data'})

            if self.data is None:
                continue

            if p == 'K':
                self.data = self.data[1:]
            else:
                self.data = self.data[2:]

            for data in self.data:
                d = dict(zip(self.keys[p],[p] + self.splitNameTeamString(data[0]) + data[1:]))
                self.projections.append(d)

    def scrape(self):
        self.cheatsheets = []
        self.projections = []
        self.scrapeProjections()
        self.scrapeCheatSheets()
        self.data = self.cheatsheets + self.projections
        return self.data

    def splitNameTeamString(self, nameTeamStr):

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

        self.assertEquals(camNewtonFound,True)
        self.assertEquals(tomBradyFound,True)

        andrewLuckFound = 0
        seattleFound = 0
        for player in s.cheatsheets:
            if player['name'] == "Andrew Luck":
                #print player
                self.assertEqual(player['team'], "IND")
                andrewLuckFound += 1

            if player['name'] == "Seattle Seahawks":
                if 'position' in player:
                    self.assertEqual(player['position'], "DEF")
                seattleFound += 1

        self.assertEquals(andrewLuckFound,4)
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