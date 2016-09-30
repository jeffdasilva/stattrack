import datetime
from multiprocessing.pool import ThreadPool
import unittest

from sitescraper.scraper import SiteScraper


class NhlCbsSportsDotComSraper(SiteScraper):

    ProjectedGamesPlayed = ['cbssports.proj.gp']
    ProjectedGoals = ['cbssports.proj.g']
    ProjectedAssists = ['cbssports.proj.a']
    ProjectedWins = ['cbssports.proj.w']
    ProjectedTies = []
    ProjectedShutouts = ['cbssports.proj.so']


    def __init__(self):
        super(NhlCbsSportsDotComSraper, self).__init__(url="http://www.cbssports.com/fantasy/hockey")
        self.maxCacheTime = datetime.timedelta(days=1)

        self.positions = ['C','RW','LW','D','G']

    def scrapeProjectionsByPosition(self,position):

        url_offset = '/stats/sortable/points/' + position + '/advanced/projections?&print_rows=9999'
        table_attrs = {'class':'data'}
        table = self.scrapeTable(urlOffset=url_offset,attrs=table_attrs, index="Projections Advanced Stats")

        table_header = table[1]
        table_data = table[2:]

        stat_type = []
        for statname in table_header:
            # special case gpp for goalies
            if statname.lower() == "ggp":
                statname = "GP"

            stat_type.append("cbssports.proj." + str(statname).lower())
        assert(len(stat_type) == len(table_header))

        data = []

        for ele in table_data:
            if len(stat_type) == len(ele):
                data.append(dict(zip(stat_type,ele)))
                assert('cbssports.proj.player' in data[-1])
                data[-1]['name'],data[-1]['team'] = data[-1]['cbssports.proj.player'].replace(u'\xa0',u'').rsplit(',',1)
                del data[-1]['cbssports.proj.player']

        return data

    def scrape(self):

        numOfThreads = len(self.positions)
        #numOfThreads = 0

        data = []

        if numOfThreads == 0:
            for p in self.positions:
                data += self.scrapeProjectionsByPosition(p)
        else:
            pool = ThreadPool(numOfThreads)
            result = pool.map(self.scrapeProjectionsByPosition,self.positions)
            pool.close()
            pool.join()

            for r in result:
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

            elif str(d['name']) == "Tuukka Rask":
                print d
                RaskFound += 1
                p = HockeyPlayer(properties=d)
                print p
                self.assertGreater(p.projectedGamesPlayed(),30)
                self.assertGreater(p.projectedGoaltenderShutOuts(), 0)
                self.assertGreater(p.projectedGoaltenderWins(),20)
                self.assertGreater(p.pointsPerGame(),1.0)

        self.assertEquals(McDavidFound,1)
        self.assertEquals(RaskFound,1)
