import datetime
import unittest

from sitescraper.scraper import SiteScraper


class FootballDBDotComScraper(SiteScraper):

    # format for fantasy stats table is
    # Year Team Att Cmp Yds TD Int 2Pt Att Yds TD 2Pt Rec Yds TD 2Pt FL TD Pts
    PassingStats = ["Passing" + stat for stat in ["Att", "Cmp", "Yds", "TD", "Int", "2Pt"] ]
    RushingStats = ["Rushing" + stat for stat in ["Att", "Yds", "TD", "2Pt" ] ]
    ReceivingStats = ["Receiving" + stat for stat in ["Rec", "Yds", "TD", "2Pt"] ]
    FumbleStats = ["FL", "TD", "Pts" ]
    Stats = ["team"] + PassingStats + RushingStats + ReceivingStats + FumbleStats

    PassingAttempts = PassingStats[0]
    PassingCompletions = PassingStats[1]
    PassingYards = PassingStats[2]
    PassingTDs = PassingStats[3]
    PassingInterceptionsThrown = PassingStats[4]
    PassingTwoPointers = PassingStats[5]

    RushingAttempts = RushingStats[0]
    RushingYards = RushingStats[1]
    RushingTDs = RushingStats[2]
    RushingTwoPointers = RushingStats[3]

    Receptions = ReceivingStats[0]
    ReceivingYards = ReceivingStats[1]
    ReceivingTDs = ReceivingStats[2]
    ReceivingTwoPointers = ReceivingStats[3]

    FumblesLost = FumbleStats[0]
    FumbleTDs = FumbleStats[1]


    def __init__(self):
        super(FootballDBDotComScraper, self).__init__(url="http://www.footballdb.com")
        self.maxCacheTime = datetime.timedelta(days=90)

    def scrape(self):

        self.historicalStats = []

        for position in [ "QB", "RB", "WR", "TE"]:
            urlOffset = "/players/current.html?pos=" + position
            playerList = self.scrapeTable(urlOffset=urlOffset,attrs={'class':'statistics'})
            playerLinks = self.link.copy()

            playerCount = 0

            if playerList is None:
                continue

            for player in playerList:

                playerCount += 1
                if self.testmode and playerCount > 5:
                    break

                if player[0] in playerLinks:
                    self.scrapeTables(urlOffset=playerLinks[player[0]], attrs={'class':'statistics'})

                    fantasyStatTbl = None
                    for tbl in self.data:
                        if len(tbl) > 2 and len(tbl[2:]) > 0 and \
                            len(FootballDBDotComScraper.Stats) == len(tbl[2:][0])-1:
                            fantasyStatTbl = tbl

                    if fantasyStatTbl is None:
                        continue

                    fantasyStatTbl = fantasyStatTbl[2:]
                    name = str(player[0]).rsplit(',',1)[1].strip() + " " + str(player[0]).rsplit(',',1)[0].strip()
                    stats = {'name':name, 'position':position}
                    for yearData in fantasyStatTbl:
                        year = yearData[0]
                        stats[year] = {}
                        stats[year] = dict(zip(FootballDBDotComScraper.Stats,yearData[1:]))

                    currentYear = str(datetime.datetime.now().year)

                    if currentYear in stats:
                        if 'team' in stats[currentYear]:
                            stats['team'] = stats[currentYear]['team']

                    #print stats
                    self.historicalStats.append(stats)

        self.data = self.historicalStats
        return self.data


class TestMyFantasyLeagueDotComScraper(unittest.TestCase):

    def testFootballDBDotComScraper(self):

        thisYear = str(datetime.datetime.now().year)

        s = FootballDBDotComScraper()
        s.testmode = True
        s.scrape()

        for d in s.data:
            print d

        for i in range(0,3):
            print "--- s.data[" + str(i) + "] ---"
            print s.data[i]
            self.assertGreater(len(s.data[i]),3)

            print s.data[i]['name']
            if 'team' in s.data[i]:
                print s.data[i]['team']
            print s.data[i]['position']
            self.assertEquals(s.data[i]['position'],'QB')
            print s.data[i][thisYear]['team']
            print s.data[i][thisYear]['PassingTD']
            self.assertGreaterEqual(int(s.data[i][thisYear]['PassingTD']),0)

if __name__ == '__main__':
    unittest.main()

