'''
Created on Sep 1, 2016

@author: jdasilva
'''
import unittest


class StatTrackParser(object):
    StatusExit = 0


    def __init__(self, league):
        self.league = league
        self.commands = []

    def promptForCommand(self):
        cmd = raw_input('% ')
        return self.parse(cmd)

    def promptForCommandLoop(self):
        while True:
            status = self.promptForCommand()
            if status == StatTrackParser.StatusExit:
                break

    def parse(self,cmd):
        return StatTrackParser.StatusExit



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


if __name__ == "__main__":
    unittest.main()