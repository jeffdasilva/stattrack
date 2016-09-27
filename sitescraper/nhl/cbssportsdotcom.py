import datetime
from multiprocessing.pool import ThreadPool
import unittest

from sitescraper.scraper import SiteScraper


class ArrudaCupCbsSportsDotComSraper(SiteScraper):

    def __init__(self):
        super(ArrudaCupCbsSportsDotComSraper, self).__init__(url="http://arruda-cup.hockey.cbssports.com/")
        #self.maxCacheTime = datetime.timedelta(seconds=1)
        self.maxCacheTime = datetime.timedelta(days=1)
        self.cookiefile = '/tools/HockeyPool/arruda-cup-cbssports.cookie.txt'


    def scrapeIndividualTeam(self,team_number):
        tableAttrs={'class':'data data3 pinHeader borderTop'}
        urlOffset = 'teams/' + str(team_number)
        team_data = self.scrapeTable(urlOffset=urlOffset,attrs=tableAttrs)
        return team_data

    def scrape(self):

        leagueData = []
        numOfThreads = 10

        if numOfThreads == 0:
            for team_i in range(1,18):
                r = self.scrapeIndividualTeam(team_i)
                if len(r) > 3:
                    leagueData.append(r[3:])
        else:
            pool = ThreadPool(numOfThreads)
            result = pool.map(self.scrapeIndividualTeam,range(1,18))
            pool.close()
            pool.join()

            for r in result:
                if r is not None and len(r) > 3:
                    leagueData.append(r[3:])

        draftedPlayers = []
        for team_i in leagueData:
            for player_i in team_i:
                if player_i is not None and len(player_i) >= 3:
                    playerNamePosTeam = player_i[2]

                if playerNamePosTeam == "EMPTY":
                    continue

                print playerNamePosTeam
                draftedPlayers.append(playerNamePosTeam)

        self.data = draftedPlayers

        return self.data

class TestArrudaCupCbsSportsDotComScraper(unittest.TestCase):

    def testArrudaCupCbsSportsDotComSraper(self):

        s = ArrudaCupCbsSportsDotComSraper()
        #s.testmode = True
        #s.debug = True
        data = s.scrape()
        print data

