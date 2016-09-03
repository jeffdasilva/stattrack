'''
Created on Sep 1, 2016

@author: jdasilva
'''
import os
import unittest

from cli.cmd.command import Command, ErrorCommand, SearchCommand


class StatTrackParser(object):
    StatusTrue = 0
    StatusFalse = 1
    StatusExit = -1
    StatusError = 2

    def __init__(self, league):
        self.league = league

        self.status = StatTrackParser.StatusTrue

        self.commands = []
        self.commands += Command.GenericCommands

        self.defaultCommand = SearchCommand()
        self.errorCommand = ErrorCommand()

        self.player_list = []
        self.undo_stack = []
        self.undoMode = False
        self.db_stack = []
        self.autosave = True

    def prompt(self):
        cmd = raw_input('% ')
        status = self.processCommandAndResponse(cmd)
        return status

    def promptLoop(self):
        while True:
            status = self.prompt()
            if status == StatTrackParser.StatusExit:
                break

    def processCommand(self,cmd):
        self.status = StatTrackParser.StatusTrue

        for commandIter in self.commands:
            if commandIter.matches(cmd):

                if commandIter.preApplyMessage(cmd, self) is not None:
                    print commandIter.preApplyMessage(cmd, self)

                return commandIter.apply(cmd, self)

        if self.defaultCommand is not None:
            return self.defaultCommand.apply(cmd, self)
        else:
            return self.error("Invalid Command")

    def processResponse(self, response, status):
        print response
        return status

    def processCommandAndResponse(self,cmd):
        response = self.processCommand(cmd)
        status = self.processResponse(response, self.status)
        return status

    def bold(self,string):
        return '\033[1m' + string + '\033[0m'

    def error(self,errorMsg):
        return self.errorCommand.apply(errorMsg,self)


class TestStatTrackParser(unittest.TestCase):

    def testConstruct(self):

        from league.league import League

        l = League("jds")
        p = StatTrackParser(l)
        self.assertNotEquals(p.league, None)
        self.assertEquals(p.league.name, l.name)
        l.name = "jds.0"
        self.assertEquals(p.league.name, l.name)
        p.league.name = "jds.1"
        self.assertEquals(p.league.name, l.name)
        self.assertEquals(l.name,"jds.1")
        pass

    def testErrorCommand(self):
        p = StatTrackParser(None)
        status = p.processCommandAndResponse("invalid command")
        self.assertEqual(status, StatTrackParser.StatusError)
        pass

    def testNoLeagueSimpleScript(self):
        p = StatTrackParser(None)

        script = []
        script.append(("help",StatTrackParser.StatusTrue))
        script.append(("",StatTrackParser.StatusTrue))
        script.append(("blank",StatTrackParser.StatusTrue))
        script.append(("error this is an error",StatTrackParser.StatusError))
        script.append(("help",StatTrackParser.StatusTrue))
        script.append(("autosave",StatTrackParser.StatusTrue))
        script.append(("help",StatTrackParser.StatusTrue))
        script.append(("autosave",StatTrackParser.StatusTrue))
        script.append(("help",StatTrackParser.StatusTrue))
        script.append(("undo",StatTrackParser.StatusTrue))
        script.append(("undo",StatTrackParser.StatusTrue))
        script.append(("undo",StatTrackParser.StatusError))
        script.append(("pop",StatTrackParser.StatusError))
        script.append(("push",StatTrackParser.StatusError))
        script.append(("echo hello world",StatTrackParser.StatusTrue))
        script.append(("print hello world",StatTrackParser.StatusTrue))
        script.append(("quit",StatTrackParser.StatusExit))
        script.append(("exit",StatTrackParser.StatusExit))
        script.append(("q",StatTrackParser.StatusExit))
        script.append(("bogus command",StatTrackParser.StatusError))
        script.append(("undo",StatTrackParser.StatusError))
        script.append(("update",StatTrackParser.StatusError))
        script.append(("pop",StatTrackParser.StatusError))

        for cmd_status in script:
            cmd = cmd_status[0]
            expectedStatus = cmd_status[1]
            print "% " + cmd
            retStatus = p.processCommandAndResponse(cmd)
            self.assertEqual(retStatus, expectedStatus)

    def testScript(self):

        from db.playerdb import PlayerDB
        from db.player.player import Player
        from league.league import League

        pDB = PlayerDB()
        pDB.saveFile = os.path.dirname(os.path.abspath(__file__)) + "/../data/test_parserplayerdb.pickle"
        pDB.add(Player("June", "Team-June"))
        pDB.add(Player("Rudy DaSilva", "Team-Rudy"))
        pDB.add(Player("Frankie", "Team-Frankie"))
        league = League(name='JDS',db=pDB)
        league.parser.defaultCommand = None

        script = []
        script.append(("help",StatTrackParser.StatusTrue))
        script.append(("push",StatTrackParser.StatusTrue))
        script.append(("pop",StatTrackParser.StatusTrue))
        script.append(("pop",StatTrackParser.StatusError))
        script.append(("undo",StatTrackParser.StatusTrue))
        script.append(("undo",StatTrackParser.StatusTrue))
        script.append(("undo",StatTrackParser.StatusError))
        script.append(("save",StatTrackParser.StatusTrue))
        script.append(("undo",StatTrackParser.StatusTrue))
        script.append(("undo",StatTrackParser.StatusError))
        script.append(("load",StatTrackParser.StatusTrue))
        script.append(("undo",StatTrackParser.StatusTrue))
        script.append(("undo",StatTrackParser.StatusError))

        script.append(("bogus command",StatTrackParser.StatusError))
        script.append(("June",StatTrackParser.StatusError))

        script.append(("search june",StatTrackParser.StatusTrue))
        script.append(("search bogus command",StatTrackParser.StatusFalse))

        for cmd_status in script:
            cmd = cmd_status[0]
            expectedStatus = cmd_status[1]
            print "% " + cmd
            retStatus = league.parser.processCommandAndResponse(cmd)
            self.assertEqual(retStatus, expectedStatus)

        league.parser.defaultCommand = SearchCommand()
        script = []
        script.append(("bogus command",StatTrackParser.StatusFalse))
        script.append(("June",StatTrackParser.StatusTrue))
        script.append(("rUdY d",StatTrackParser.StatusTrue))
        script.append(("search u",StatTrackParser.StatusTrue))
        script.append(("ls",StatTrackParser.StatusTrue))


        for cmd_status in script:
            cmd = cmd_status[0]
            expectedStatus = cmd_status[1]
            print "% " + cmd
            retStatus = league.parser.processCommandAndResponse(cmd)
            self.assertEqual(retStatus, expectedStatus)


if __name__ == "__main__":
    unittest.main()