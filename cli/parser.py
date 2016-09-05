'''
Created on Sep 1, 2016

@author: jdasilva
'''
import os
import unittest

from cli.cmd.command import Command, SearchCommand


class StatTrackParser(object):
    StatusTrue = 0
    StatusFalse = 1
    StatusExit = -1
    StatusError = 2

    def __init__(self, league):
        self.league = league
        self.status = StatTrackParser.StatusTrue
        self.commands = Command.GenericCommands
        self.player_list = []
        self.undo_stack = []
        self.undoMode = False
        self.db_stack = []
        self.autosave = False
        self.debug = False
        self.defaultCommand = self.getCommand("search")
        self.db_requires_save = False

    def recvInput(self, prompt):
        return raw_input(prompt)

    def sendOutput(self, output):
        print output

    def sendDebugOutput(self, output):
        if self.debug: self.sendOutput("DEBUG: " + output)

    def prompt(self):
        cmd = self.recvInput('% ')
        status = self.processCommandAndResponse(cmd)
        return status

    def promptLoop(self):
        while True:
            status = self.prompt()
            if status == StatTrackParser.StatusExit:
                break

    def getCommand(self,cmd):
        for commandIter in self.commands:
            if commandIter.matches(cmd):
                return commandIter
        return None

    def processCommand(self,cmd):
        self.status = StatTrackParser.StatusTrue

        command = self.getCommand(cmd)

        if command is not None:
            if command.preApplyMessage(cmd, self) is not None:
                self.sendOutput(command.preApplyMessage(cmd, self))

            if command.updatesDB:
                self.db_requires_save = True

            return command.apply(cmd, self)

        if self.defaultCommand is not None:
            if self.defaultCommand.updatesDB:
                self.db_requires_save = True
            return self.defaultCommand.apply(cmd, self)
        else:
            return self.error("Invalid Command")

    def processResponse(self, response, status):
        self.sendOutput(response)
        return status

    def processCommandAndResponse(self,cmd):
        response = self.processCommand(cmd)
        status = self.processResponse(response, self.status)

        if self.autosave and self.db_requires_save:
            if status != StatTrackParser.StatusError:
                if self.league is not None and self.league.db is not None:
                    self.undoMode = True
                    self.save()
                    self.undoMode = False
                    self.sendDebugOutput("[autosave]")

        return status

    def bold(self,string):
        return '\033[1m' + string + '\033[0m'

    def error(self,errorMsg):
        return self.getCommand("error").apply(errorMsg,self)

    def pushOnUndoStack(self,cmd):
        if not self.undoMode:
            self.undo_stack.append(cmd)

    def pushState(self):
        return self.getCommand("push").apply("push",self)

    def save(self):
        return self.getCommand("save").apply("save",self)

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

    def executeTestScript(self,script,parser):
        for cmd_status in script:
            cmd = cmd_status[0]
            expectedStatus = cmd_status[1]
            print "% " + cmd
            retStatus = parser.processCommandAndResponse(cmd)
            self.assertEqual(retStatus, expectedStatus)


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
        self.executeTestScript(script,p)


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
        league.parser.debug = True

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

        self.executeTestScript(script,league.parser)

        self.assertEquals(len(league.parser.player_list),0)

        league.parser.defaultCommand = SearchCommand()
        script = []
        script.append(("bogus command",StatTrackParser.StatusFalse))
        script.append(("June",StatTrackParser.StatusTrue))
        script.append(("rUdY d",StatTrackParser.StatusTrue))
        script.append(("search u",StatTrackParser.StatusTrue))
        script.append(("ls",StatTrackParser.StatusTrue))
        script.append(("help",StatTrackParser.StatusTrue))
        script.append(("save",StatTrackParser.StatusTrue))
        script.append(("undo",StatTrackParser.StatusTrue))
        script.append(("undo",StatTrackParser.StatusError))
        script.append(("search",StatTrackParser.StatusTrue))

        self.executeTestScript(script,league.parser)

        self.assertEquals(len(league.parser.player_list),3)

        script = []
        script.append(("save",StatTrackParser.StatusTrue))
        script.append(("ls",StatTrackParser.StatusTrue))
        script.append(("draft",StatTrackParser.StatusTrue))
        script.append(("ls",StatTrackParser.StatusTrue))
        script.append(("draft",StatTrackParser.StatusTrue))
        script.append(("ls",StatTrackParser.StatusTrue))
        script.append(("draft Frank",StatTrackParser.StatusTrue))
        script.append(("draft Frank",StatTrackParser.StatusError))
        script.append(("ls",StatTrackParser.StatusFalse))
        script.append(("undo",StatTrackParser.StatusTrue))
        script.append(("search",StatTrackParser.StatusTrue))

        script.append(("draft 1",StatTrackParser.StatusError))
        script.append(("draft 0",StatTrackParser.StatusTrue))
        script.append(("undo",StatTrackParser.StatusTrue))

        script.append(("undraft Rudy",StatTrackParser.StatusTrue))
        script.append(("search",StatTrackParser.StatusTrue))
        script.append(("draft 2",StatTrackParser.StatusError))
        script.append(("draft 1",StatTrackParser.StatusTrue))
        script.append(("draft",StatTrackParser.StatusTrue))
        script.append(("undraft Frankie",StatTrackParser.StatusTrue))
        script.append(("undraft Frankie",StatTrackParser.StatusTrue))

        script.append(("help",StatTrackParser.StatusTrue))

        script.append(("search",StatTrackParser.StatusTrue))
        self.executeTestScript(script,league.parser)
        self.assertEquals(len(league.parser.player_list),1)

        script = []
        script.append(("load",StatTrackParser.StatusTrue))
        script.append(("search",StatTrackParser.StatusTrue))
        self.executeTestScript(script,league.parser)
        self.assertEquals(len(league.parser.player_list),3)

        script = []
        script.append(("search",StatTrackParser.StatusTrue))
        script.append(("push",StatTrackParser.StatusTrue))
        script.append(("draft Rudy",StatTrackParser.StatusTrue))
        script.append(("draft June",StatTrackParser.StatusTrue))
        script.append(("search",StatTrackParser.StatusTrue))
        script.append(("pop",StatTrackParser.StatusTrue))
        script.append(("search",StatTrackParser.StatusTrue))
        self.executeTestScript(script,league.parser)
        self.assertEquals(len(league.parser.player_list),3)

        script = []
        script.append(("search",StatTrackParser.StatusTrue))
        script.append(("draft Rudy",StatTrackParser.StatusTrue))
        script.append(("draft June",StatTrackParser.StatusTrue))
        script.append(("save",StatTrackParser.StatusTrue))
        script.append(("undo",StatTrackParser.StatusTrue))
        script.append(("undo",StatTrackParser.StatusTrue))
        script.append(("undo",StatTrackParser.StatusTrue))
        script.append(("search",StatTrackParser.StatusTrue))
        script.append(("load",StatTrackParser.StatusTrue))
        script.append(("search",StatTrackParser.StatusTrue))
        self.executeTestScript(script,league.parser)
        self.assertEquals(len(league.parser.player_list),1)

        script = []
        script.append(("search",StatTrackParser.StatusTrue))
        script.append(("undraft Rudy DaSilva",StatTrackParser.StatusTrue))
        script.append(("undraft June",StatTrackParser.StatusTrue))
        script.append(("search",StatTrackParser.StatusTrue))
        script.append(("ignore 2",StatTrackParser.StatusTrue))
        script.append(("undo",StatTrackParser.StatusTrue))
        script.append(("search",StatTrackParser.StatusTrue))
        script.append(("ignore",StatTrackParser.StatusTrue))
        script.append(("undo",StatTrackParser.StatusTrue))

        script.append(("ignore Frank",StatTrackParser.StatusTrue))
        script.append(("ignore Frank",StatTrackParser.StatusError))

        script.append(("search",StatTrackParser.StatusTrue))

        self.executeTestScript(script,league.parser)
        self.assertEquals(len(league.parser.player_list),2)



if __name__ == "__main__":
    unittest.main()