#!/usr/bin/env python2

'''
@author: jdasilva
'''
import unittest

from league.custom.irongut import IronGutFootballLeague
from league.custom.oleague import OLeagueFootballLeague
from league.custom.arrudacup import ArrudaCupHockeyLeague
from league.custom.oracle import OracleFootballLeague

class StatTrack(object):
    StatTrackMajorVersion = 0
    StatTrackMinorVersion = 59
    StatTrackBuildNumber = 150

    def __init__(self):
        #self.league = "ArrudaCup"
        #self.league = "OLeague"
        #self.league = "IronGut"
        self.league = "Oracle"

    def getVersion(self):
        return str(StatTrack.StatTrackMajorVersion) + "." + str(StatTrack.StatTrackMinorVersion)

    def getFullVersionString(self):
        return "[Version: " + self.getVersion() + ", " + \
            "Build: " + str(StatTrack.StatTrackBuildNumber) + "]"

    def printBanner(self):
        print("StatTrack\t" + self.getFullVersionString())
        print(" https://github.com/jeffdasilva/stattrack")
        print
        print("Type 'help' to list available commands")
        print
        print(" LEAGUE: " + self.league)
        print

    def run(self):

        if self.league == "OLeague":
            self.printBanner()
            l = OLeagueFootballLeague()
        elif self.league == "ArrudaCup":
            self.printBanner()
            l = ArrudaCupHockeyLeague()
        elif self.league == "IronGut":
            self.printBanner()
            l = IronGutFootballLeague()
        elif self.league == "Oracle":
            self.printBanner()
            l = OracleFootballLeague()
        else:
            print("ERROR: Unknown League '" + self.league + "'")
            return

        l.draftmode()

class StatTrackTest(unittest.TestCase):

    def testConstructor(self):
        s = StatTrack()
        self.assertEquals(s.getVersion(), str(StatTrack.StatTrackMajorVersion) + "." + str(StatTrack.StatTrackMinorVersion))
        print(s.getFullVersionString())
        #s.run()

if __name__ == '__main__':
    st = StatTrack()
    st.run()
