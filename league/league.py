'''
Created on Sep 1, 2016

@author: jdasilva
'''
import unittest

from cli.parser import StatTrackParser

class League():

    def __init__(self, name, db=None, rules=None):

        self.name = name
        self.db = db
        self.rules = rules
        self.parser = StatTrackParser(self)

        self.player_list = []
        self.undo_stack = []
        self.db_stack = []
        self.autosave = True


class LeagueTest(unittest.TestCase):

    def testConstruct(self):

        l = League("foo")
        self.assertEquals(l.name,"foo")
        self.assertEquals(l.db, None)
        pass


if __name__ == "__main__":
    unittest.main()