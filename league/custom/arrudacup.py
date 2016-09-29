
import copy
import unittest

from db.hockeydb import HockeyPlayerDB
from league.hockey import HockeyLeague
from league.rules import HockeyRules


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

        self.scrapers = [TsnDotCaScraper(), ArrudaCupCbsSportsDotComSraper()]

        self.enable_rotoworld_scraper = True

    def update(self):

        self.db.wget(self.scrapers)


    def factoryReset(self):

        self.db = HockeyPlayerDB(self.name)
        self.update()

        if self.enable_rotoworld_scraper:
            from sitescraper.multisport.rotoworlddotcom import RotoWorldDotComScraper

            rotoScrape = RotoWorldDotComScraper()
            for p in self.db.player:
                #print "RotoWorld: Learning about " + self.db.player[p].name + "..."
                pStats = rotoScrape.scrape(playerName=self.db.player[p].name, league="nhl")
                if pStats is not None:
                    self.db.player[p].update(pStats)



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
        l.enable_rotoworld_scraper = False
        l.factoryReset()

        for player in l.db.player:
            print l.db.player[player]

        # test that deep copy operation works
        stack = []
        stack.append(copy.deepcopy(l.db))

        #p = l.db.player["aaron rodgers - gb"]
        #self.assertEqual(p.passingTwoPointers(year=2015),4)
        #print p
        #print "Passing Attempts: " + str(p.passingAttempts())
        #print "Passing TDs: " + str(p.projectedPassingTDs())


if __name__ == "__main__":
    unittest.main()
