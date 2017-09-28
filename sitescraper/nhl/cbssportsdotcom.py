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
        self.maxCacheTime = datetime.timedelta(days=7)
        self.positions = ['C','RW','LW','D','G']
        self.retries = 2

    def scrapeProjectionsByPosition(self,position):

        if position not in self.positions:
            raise ValueError("Error: Postition " + position + " is not a valid position")

        url_offset = '/fantasy/hockey/stats/sortable/points/' + position + '/advanced/projections?&print_rows=9999'

        table_attrs = {'class':'data compact'}
        table = self.scrapeTable(urlOffset=url_offset,attrs=table_attrs)
        links = self.scrapeLinks(urlOffset=url_offset)

        if table is None:
            raise ValueError('table is None')

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
                    link = links[data[-1]['name']]
                    if not link.startswith(self.url):
                        link = self.url + link

                    data[-1][NhlCbsSportsDotComSraper.es.link()] = link

                data[-1]['scraper'] = [NhlCbsSportsDotComSraper.es.prefix]

        return data

    def scrape(self):

        numOfThreads = len(self.positions)
        results = self.scrapeWithThreadPool(self.scrapeProjectionsByPosition,self.positions,numOfThreads)

        data = []
        for r in results:
            data += r

        return data

    def getUrlOffset(self,url):
        if url.startswith(self.url):
            urlOffset = url[len(self.url):]
        else:
            raise ValueError('Unexpected player link found in ' + self.url + ' scraper: ' + url )
        return urlOffset

    def scrapePlayer(self,player):

        if NhlCbsSportsDotComSraper.es.link() not in player.property:
            return None

        url = player.property[NhlCbsSportsDotComSraper.es.link()]

        urlOffset = self.getUrlOffset(url)
        data = SiteScraper.scrape(self,urlOffset=urlOffset)
        if data is None:
            return None

        stat_properties = {}
        for stat in data.findAll("span", attrs={'class':'stats'}):
            stat = stat.text.strip()
            if len(stat) == 0 or ': ' not in stat:
                continue

            stat_name,stat_data = stat.split(': ',1)

            stat_name = NhlCbsSportsDotComSraper.es.sanitize(stat_name)
            stat_properties[stat_name] = stat_data

        links = SiteScraper.scrapeLinks(self,urlOffset=urlOffset)
        if 'FULL CAREER STATS' in links:
            stat_properties[NhlCbsSportsDotComSraper.es.link('CareerStats')] = self.url + links['FULL CAREER STATS']

        player.update(stat_properties)

        self.scrapePlayerCareerStats(player)

        return stat_properties

    def scrapePlayerCareerStats(self,player):

        if NhlCbsSportsDotComSraper.es.link('CareerStats') not in player.property:
            return None

        url = player.property[NhlCbsSportsDotComSraper.es.link('CareerStats')]
        urlOffset = self.getUrlOffset(url)
        data = self.scrapeTable(urlOffset=urlOffset, attrs={'class':'data compact'},index="YEAR")

        if data is None or len(data) < 2:
            return None

        stat_categories = NhlCbsSportsDotComSraper.es.sanitize(data[0])
        stats = data[1:]

        career_stats_dict = {}

        for stat in stats:
            stat_dict_entry = dict(zip(stat_categories,stat))
            assert('year' in stat_dict_entry)
            career_stats_dict[stat_dict_entry['year']] = stat_dict_entry

        player.update({NhlCbsSportsDotComSraper.es.stats():career_stats_dict})


    def scrapePlayerList(self,playerList):
        results = self.scrapeWithThreadPool(self.scrapePlayer,playerList)
        return results


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

                p.projected_games_played_attr += NhlCbsSportsDotComSraper.ProjectedGamesPlayed
                p.projected_wins_attr += NhlCbsSportsDotComSraper.ProjectedWins

                self.assertGreater(p.projectedGamesPlayed(),30)
                #self.assertGreater(p.projectedGoaltenderShutOuts(), 0)
                self.assertGreater(p.projectedGoaltenderWins(),20)
                self.assertGreater(p.pointsPerGame(),0.5)
                self.assertTrue('G' in p.position)

                self.assertEqual(p.age(),'?')
                s.scrapePlayerList([p])
                self.assertNotEqual(p.age(),'?')
                self.assertGreaterEqual(int(p.age()),29)
                print p.property[NhlCbsSportsDotComSraper.es.link('CareerStats')]


        self.assertEquals(McDavidFound,1)
        self.assertEquals(RaskFound,1)
