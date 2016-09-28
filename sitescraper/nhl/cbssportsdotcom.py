import datetime
from multiprocessing.pool import ThreadPool
import unittest

from sitescraper.scraper import SiteScraper

class ArrudaCupCbsSportsDotComSraper(SiteScraper):


    def __init__(self):
        super(ArrudaCupCbsSportsDotComSraper, self).__init__(url="http://arruda-cup.hockey.cbssports.com/")
        #self.maxCacheTime = datetime.timedelta(seconds=60)
        self.maxCacheTime = datetime.timedelta(days=1)
        self.cookiefile = '/tools/HockeyPool/arruda-cup-cbssports.cookie.txt'

        self.team = {}
        self.team[1] = "Brian"
        self.team[2] = "Ferd"
        self.team[3] = "Will"
        self.team[4] = "Dave"
        self.team[5] = "Donny"
        self.team[6] = "Mike"
        self.team[7] = "Jeff"
        self.team[8] = "Alex"
        self.team[9] = "Al"
        self.team[10] = "Ryan"
        self.team[11] = "Clent"
        self.team[12] = "Steve"
        self.team[13] = "Greg"
        self.team[14] = "Jeremy"
        self.team[15] = "Jad"
        self.team[16] = "Johnny"
        self.team[17] = "Art"
        self.team[18] = "Fab"

    def scrapeIndividualTeam(self,team_number):
        urlOffset = 'teams/' + str(team_number)

        playerTableAttrs={'class':'data data3 pinHeader borderTop'}
        team_data = self.scrapeTable(urlOffset=urlOffset,attrs=playerTableAttrs)

        goalieTableAttrs={'class':'data pinHeader'}
        team_data += self.scrapeTable(urlOffset=urlOffset,attrs=goalieTableAttrs)

        return team_data

    def scrape(self):

        leagueData = []
        numOfThreads = 6

        if numOfThreads == 0:
            for team_i in self.team:
                r = self.scrapeIndividualTeam(team_i)
                if len(r) > 3:
                    leagueData.append(r[3:])
        else:
            pool = ThreadPool(numOfThreads)
            result = pool.map(self.scrapeIndividualTeam,self.team.keys())
            pool.close()
            pool.join()

            for r in result:
                if r is not None and len(r) > 3:
                    leagueData.append(r[3:])

        draftedPlayers = []
        for team_payload,team_key in zip(leagueData,self.team):
            for player in team_payload:
                if player is not None and len(player) >= 3:
                    playerNamePosTeam = player[2]

                if not isinstance(playerNamePosTeam, basestring):
                    continue

                if playerNamePosTeam == "EMPTY":
                    continue

                playerNamePosTeam = playerNamePosTeam.rsplit(' | ',1)

                if len(playerNamePosTeam) > 1:
                    team = playerNamePosTeam[1]
                else:
                    team = "???"

                name,position = playerNamePosTeam[0].rsplit(' ',1)

                player_data = {}
                player_data['name'] = name
                player_data['team'] = team
                player_data['position'] = position
                player_data['isDrafted'] = True
                player_data['owner'] = self.team[team_key]

                #print player_data
                draftedPlayers.append(player_data)

        return draftedPlayers

class TestArrudaCupCbsSportsDotComScraper(unittest.TestCase):

    def testArrudaCupCbsSportsDotComSraper(self):
        from db.playerdb import PlayerDB
        from db.player.player import Player

        s = ArrudaCupCbsSportsDotComSraper()
        data = s.scrape()
        self.assertNotEqual(data, None)
        print data

        db = PlayerDB(name="ArrudaCupTest", verbose=True)
        for player_data in data:
            self.assertNotEqual(player_data, None)
            #print player_data
            p = Player(properties=player_data)

            self.assertEquals(p.isDrafted, True)
            self.assertNotEqual(p, None)
            #print p
            #print p.key()
            db.add(p)

        self.assertEquals(db.numberOfPlayersDrafted(),len(data))


    def testNoTeamDuplicates(self):
        s = ArrudaCupCbsSportsDotComSraper()
        self.assertEquals(len(s.team), 18)
        self.assertEquals(len(s.team.values()),len(set(s.team.values())),"Duplicate team name values exist!")


