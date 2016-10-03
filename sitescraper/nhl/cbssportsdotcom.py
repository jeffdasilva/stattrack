import datetime
import unittest

from db.player.strings import HockeyPlayerStrings
from sitescraper.scraper import SiteScraper


class NhlCbsSportsDotComSraper(SiteScraper):

    es = HockeyPlayerStrings('cbssports')

    ProjStatMap = {
        'gp'     : es.projectedGamesPlayed(),
        'ggp'    : es.projectedGamesPlayed(),
        'g'      : es.projectedGoals(),
        'a'      : es.projectedAssists(),
        'w'      : es.projectedWins(),
        'so'     : es.projectedShutouts(),
    }

    ProjectedGamesPlayed = [es.projectedGamesPlayed()]
    ProjectedGoals = [es.projectedGoals()]
    ProjectedAssists = [es.projectedAssists()]
    ProjectedWins = [es.projectedWins()]
    ProjectedTies = [es.projectedTies()]
    ProjectedShutouts = [es.projectedShutouts()]

    def __init__(self):
        super(NhlCbsSportsDotComSraper, self).__init__(url="http://www.cbssports.com")
        self.maxCacheTime = datetime.timedelta(days=3)
        self.positions = ['C','RW','LW','D','G']


    def scrapeProjectionsByPosition(self,position):

        url_offset = '/fantasy/hockey/stats/sortable/points/' + position + '/advanced/projections?&print_rows=9999'
        table_attrs = {'class':'data'}
        table = self.scrapeTable(urlOffset=url_offset,attrs=table_attrs, index="Projections Advanced Stats")
        links = self.scrapeLinks(urlOffset=url_offset)

        table_header = table[1]
        table_data = table[2:]

        stat_type = []
        for statname in table_header:
            if statname.lower() in NhlCbsSportsDotComSraper.ProjStatMap:
                stat_type.append(NhlCbsSportsDotComSraper.ProjStatMap[statname.lower()])
            else:
                stat_type.append(NhlCbsSportsDotComSraper.es.projectedString(statname.lower()))

        assert(len(stat_type) == len(table_header))

        data = []

        for ele in table_data:
            if len(stat_type) == len(ele):
                data.append(dict(zip(stat_type,ele)))
                assert(NhlCbsSportsDotComSraper.es.projectedString('player') in data[-1])
                data[-1]['name'],data[-1]['team'] = data[-1][NhlCbsSportsDotComSraper.es.projectedString('player')].replace(u'\xa0',u'').rsplit(',',1)
                del data[-1][NhlCbsSportsDotComSraper.es.projectedString('player')]
                data[-1]['position'] = position

                if data[-1]['name'] in links:
                    data[-1][NhlCbsSportsDotComSraper.es.projectedString('link')] = self.url + links[data[-1]['name']]

                data[-1]['scraper'] = [NhlCbsSportsDotComSraper.es.prefix]

        return data

    def scrape(self):

        numOfThreads = len(self.positions)
        results = self.scrapeWithThreadPool(self.scrapeProjectionsByPosition,self.positions,numOfThreads)

        data = []
        for r in results:
            data += r

        return data


class TestNhlCbsSportsDotComSraper(unittest.TestCase):

    def testNhlCbsSportsDotComSraper(self):

        from db.player.hockey import HockeyPlayer

        s = NhlCbsSportsDotComSraper()
        s.testmode = True
        s.debug = True
        data = s.scrapeProjectionsByPosition('C')
        self.assertGreater(len(data), 50)

        data = s.scrape()
        self.assertGreater(len(data), 550)

        McDavidFound = 0
        RaskFound = 0
        for d in data:

            if str(d['name']) == "Connor McDavid":
                print d
                McDavidFound += 1
                self.assertEqual(d['position'], 'C')

            elif str(d['name']) == "Tuukka Rask":
                print d
                RaskFound += 1
                p = HockeyPlayer(properties=d)
                print p
                self.assertGreater(p.projectedGamesPlayed(),30)
                self.assertGreater(p.projectedGoaltenderShutOuts(), 0)
                self.assertGreater(p.projectedGoaltenderWins(),20)
                self.assertGreater(p.pointsPerGame(),1.0)
                self.assertTrue('G' in p.position)


        self.assertEquals(McDavidFound,1)
        self.assertEquals(RaskFound,1)
