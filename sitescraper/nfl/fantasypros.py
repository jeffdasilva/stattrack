
import unittest
from sitescraper.scraper import SiteScraper

class FantasyProsDotComScraper(SiteScraper):

    def __init__(self):
        super(SiteScraper, self).__init__()
        self.setProjectionURLs()
        self.setCheatSheetURLs()

    def setProjectionURLs(self):
        url_base = "http://www1.fantasypros.com/nfl/projections/"
        url_suffix = "?week=draft"

        self.projectionsURL = {}
        for p in ['QB', 'RB', 'WR', 'TE', 'K']:
            self.projectionsURL[p] = url_base + p.lower() + ".php" + url_suffix

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
        url_base = "http://www1.fantasypros.com/nfl/rankings/"
        url_suffix = "-cheatsheets.php"

        self.cheatsheetURL = {}
        for p in [ 'QB', 'RB', 'WR', 'TE', 'K', 'dst', 'consensus', 'ppr', 'half-point-ppr' ]:
            self.cheatsheetURL[p] = url_base + p.lower() + url_suffix

    def scrapeCheatSheets(self):

        self.cheatsheets = []

        for p in self.cheatsheetURL:
            s = SiteScraper(self.cheatsheetURL[p])
            #print s.url
            s.scrapeTable({'id': 'data'})

            if s.tableData is None:
                print "ERROR: table for " + p + " from " + self.cheatsheetURL[p] + " could not be extracted"
                continue

            s.tableData = s.tableData[1:]

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

            for data in s.tableData:
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
            s = SiteScraper(self.projectionsURL[p])
            s.scrapeTable({'id': 'data'})

            if s.tableData is None:
                continue

            if p == 'K':
                s.tableData = s.tableData[1:]
            else:
                s.tableData = s.tableData[2:]

            for data in s.tableData:
                d = dict(zip(self.keys[p],[p] + self.splitNameTeamString(data[0]) + data[1:]))
                self.projections.append(d)

    def scrape(self):
        self.scrapeProjections()
        self.scrapeCheatSheets()

    def splitNameTeamString(self, nameTeamStr):

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
        for player in s.projections:
            if player['name'] == "Cam Newton":
                #print player
                self.assertGreater(player['passingYards'], 2000)
                self.assertGreater(player['rushingYards'], 200)
                self.assertEqual(player['team'], "CAR")
                self.assertEqual(player['position'], "QB")
                self.assertEquals(camNewtonFound,False)
                camNewtonFound = True
        # site sometimes doesn't work
        #self.assertEquals(camNewtonFound,True)

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