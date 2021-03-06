#!/usr/bin/env python

import unittest


class League(object):

    def __init__(self, name, db=None, rules=None):
        from cli.parser import StatTrackParser

        self.name = name
        self.db = db
        self.rules = rules
        self.parser = StatTrackParser(self)
        self.property = {"isAuctionDraft":"false"}

    def draftmode(self):
        self.parser.promptLoop()

    def update(self):
        raise NotImplementedError

    def factoryReset(self):
        raise ValueError('factoryReset is not implemented')


class LeagueTest(unittest.TestCase):

    def testConstruct(self):

        l = League("foo")
        self.assertEquals(l.name,"foo")
        self.assertEquals(l.db, None)
        self.assertEquals(l.property['isAuctionDraft'], 'false')
        pass


if __name__ == "__main__":
    unittest.main()