import datetime
from multiprocessing.pool import ThreadPool
import unittest

from sitescraper.scraper import SiteScraper


class NhlCbsSportsDotComSraper(SiteScraper):


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

        data = []

        for ele in table_data:
            if len(table_header) == len(ele):
                data.append(dict(zip(table_header,ele)))
                assert('Player' in data[-1])
                data[-1]['name'],data[-1]['team'] = data[-1]['Player'].encode('utf-8').rsplit(',',1)
                del data[-1]['Player']
                #print data[-1]['name'] + ", " + data[-1]['team']
                #print data[-1]

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

        s = NhlCbsSportsDotComSraper()
        s.testmode = True
        s.debug = True
        data = s.scrapeProjectionsByPosition('C')
        self.assertGreater(len(data), 50)

        data = s.scrape()

        for d in data:
            print d

        self.assertGreater(len(data), 550)
