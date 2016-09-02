'''
Created on Sep 1, 2016

@author: jdasilva
'''
import unittest

from cli.cmd.command import ErrorCommand


class StatTrackParser(object):
    StatusTrue = 0
    StatusFalse = 1
    StatusExit = -1
    StatusError = 2

    def __init__(self, league):
        self.league = league

        self.status = StatTrackParser.StatusTrue

        self.commands = []
        self.defaultCommand = None
        self.errorCommand = ErrorCommand()

        self.player_list = []
        self.undo_stack = []
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
                return commandIter.apply(cmd, self)

        if self.defaultCommand is not None:
            return self.defaultCommand.apply(cmd)
        else:
            return self.errorCommand.apply("Invalid Command",self)

    def processResponse(self, response, status):
        print response
        return status

    def processCommandAndResponse(self,cmd):
        response = self.processCommand(cmd)
        status = self.processResponse(response, self.status)
        return status



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


if __name__ == "__main__":
    unittest.main()