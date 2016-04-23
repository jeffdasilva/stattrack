import unittest
from sitescraper.scraper import SiteScraper

class FootballDBDotComScraper(SiteScraper):

    # format for fantasy stats table is
    # Year Team Att Cmp Yds TD Int 2Pt Att Yds TD 2Pt Rec Yds TD 2Pt FL TD Pts
    PassingStats = ["Passing" + stat for stat in ["Att", "Cmp", "Yds", "TD", "Int", "2Pt"] ]
    RushingStats = ["Rushing" + stat for stat in ["Att", "Yds", "TD", "2Pt" ] ]
    ReceivingStats = ["Receiving" + stat for stat in ["Rec", "Yds", "TD", "2Pt"] ]
    MiscStats = ["FL", "TD", "Pts" ]
    Stats = ["team"] + PassingStats + RushingStats + ReceivingStats + MiscStats

    def __init__(self):
        super(FootballDBDotComScraper, self).__init__(url="http://www.footballdb.com")
        self.testmode = False


    def scrape(self):

        self.historicalStats = []

        for position in [ "QB", "RB", "WR", "TE"]:
            urlOffset = "/players/current.html?pos=" + position
            playerList = self.scrapeTable(urlOffset=urlOffset,attrs={'class':'statistics scrollable'})

            playerCount = 0

            for player in playerList:

                playerCount += 1
                if self.testmode and playerCount > 3:
                    break

                if player[0] in self.link:
                    s = SiteScraper(self.url + self.link[player[0]])
                    s.scrapeTable(attrs={'class':'statistics scrollable'},index=-1)
                    s.data = s.data[2:]
                    stats = {'name':player[0], 'position':position}
                    for yearData in s.data:
                        year = yearData[0]
                        #print year
                        stats[year] = {}
                        stats[year] = dict(zip(FootballDBDotComScraper.Stats,yearData[1:]))

                    #print stats
                    self.historicalStats.append(stats)

        self.data = self.historicalStats
        return self.data


class TestMyFantasyLeagueDotComScraper(unittest.TestCase):

    def testFootballDBDotComScraper(self):

        s = FootballDBDotComScraper()
        s.testmode = True
        s.scrape()

        #for d in s.data:
        #    print d
        self.assertGreater(len(s.data[0]),6)


        print s.data[0]['name']
        print s.data[0]['position']
        self.assertEquals(s.data[0]['position'],'QB')
        print s.data[0]['2016']['team']
        print s.data[0]['2016']['PassingTD']
        self.assertGreaterEqual(int(s.data[0]['2016']['PassingTD']),0)



if __name__ == '__main__':
    unittest.main()

