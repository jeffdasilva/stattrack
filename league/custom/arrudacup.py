
import copy
import unittest

from db.hockeydb import HockeyPlayerDB
from league.hockey import HockeyLeague
from league.rules import HockeyRules
from sitescraper.nhl.cbssportsdotcom import NhlCbsSportsDotComSraper


class ArrudaCupHockeyRules(HockeyRules):

    def __init__(self):
        super(ArrudaCupHockeyRules, self).__init__()

        self.settingsURL = "http://arruda-cup.hockey.cbssports.com/rules"
        self.numTeams = 18
        self.numForwards = 8
        self.numDefensmen = 5
        self.numGoalies = 2
        self.numReserves = 4

class ArrudaCupHockeyLeague(HockeyLeague):
    def __init__(self):
        from cli.cmd.command import SearchByPositionCommand, DraftedByCommand
        from sitescraper.nhl.tsndotca import TsnDotCaScraper
        from sitescraper.fantasy.arrudacupcbssportsdotcom import ArrudaCupCbsSportsDotComSraper

        name = "ArrudaCup"
        rules = ArrudaCupHockeyRules()
        db = HockeyPlayerDB(name)
        super(ArrudaCupHockeyLeague, self).__init__(name, db, rules)
        db.load()

        allCommand = SearchByPositionCommand('all')
        allCommand.aliases += ['a']
        self.parser.commands.append(allCommand)

        forwardsCommand = SearchByPositionCommand('forwards', positionSearchString='F')
        forwardsCommand.aliases += ['f','forward']
        self.parser.commands.append(forwardsCommand)

        defenseCommand = SearchByPositionCommand('defense', positionSearchString='D')
        defenseCommand.aliases += ['defence','def','defensemen','defencemen']
        self.parser.commands.append(defenseCommand)

        goaliesCommand = SearchByPositionCommand('goalies', positionSearchString='G')
        goaliesCommand.aliases += ['goalie','g','goaltenders','goaltender']
        self.parser.commands.append(goaliesCommand)

        draftedByCommand = DraftedByCommand()
        self.parser.commands.append(draftedByCommand)

        self.parser.autosave = False

        self.scrapers = [TsnDotCaScraper(), ArrudaCupCbsSportsDotComSraper(),NhlCbsSportsDotComSraper()]

        self.enable_rotoworld_player_scraper = True
        self.enable_cbssports_player_scraper = True

    def update(self):

        self.db.wget(self.scrapers)


    def factoryReset(self):

        self.db = HockeyPlayerDB(self.name)
        self.update()

        if self.enable_cbssports_player_scraper:
            cbssportsScrape = NhlCbsSportsDotComSraper()
            cbssportsScrape.scrapePlayerList(self.db.get(listDrafted=True, listIgnored=False))

        #self.enable_rotoworld_player_scraper = False
        if self.enable_rotoworld_player_scraper:
            from sitescraper.multisport.rotoworlddotcom import RotoWorldDotComScraper
            rotoScrape = RotoWorldDotComScraper(league='nhl')
            #rotoScrape.debug = True

            players = []
            for p in self.db.player:
                players.append(self.db.player[p].name)

            numOfThreads = 10
            statResults = rotoScrape.scrapeWithThreadPool(rotoScrape.scrape, players, numOfThreads)

            assert(len(self.db.player) == len(statResults))
            for p, pStat in zip(self.db.player,statResults):
                if pStat is not None:
                    self.db.player[p].update(pStat)


class ArrudaCupHockeyLeagueTest(unittest.TestCase):

    def testConstructor(self):
        l = ArrudaCupHockeyLeague()
        self.assertNotEquals(l, None)
        self.assertEquals(l.property['isAuctionDraft'], 'false')
        self.assertEquals(l.name,"ArrudaCup")
        self.assertNotEquals(l.rules,None)
        print str(l.rules.numForwards)

    def testLeagueDB(self):
        l = ArrudaCupHockeyLeague()
        l.enable_rotoworld_player_scraper = False
        l.enable_cbssports_player_scraper = False
        l.factoryReset()

        for player in l.db.player:
            print l.db.player[player]

        # test that deep copy operation works
        stack = []
        stack.append(copy.deepcopy(l.db))

if __name__ == "__main__":
    unittest.main()
