#!/usr/bin/env python

'''
@author: jdasilva
'''
import unittest


class StatTrack(object):
    StatTrackMajorVersion = 0
    StatTrackMinorVersion = 35
    StatTrackBuildNumber = 85

    def __init__(self):
        self.league = "ArrudaCup"
        #self.league = "OLeague"

    def getVersion(self):
        return str(StatTrack.StatTrackMajorVersion) + "." + str(StatTrack.StatTrackMinorVersion)

    def getFullVersionString(self):
        return "[Version: " + self.getVersion() + ", " + \
            "Build: " + str(StatTrack.StatTrackBuildNumber) + "]"

    def printBanner(self):
        print "StatTrack\t" + self.getFullVersionString()
        print " https://github.com/jeffdasilva/stattrack"
        print
        print

    def run(self):
        from league.custom.oleague import OLeagueFootballLeague
        from league.custom.arrudacup import ArrudaCupHockeyLeague

        if self.league == "OLeague":
            self.printBanner()
            l = OLeagueFootballLeague()
        elif self.league == "ArrudaCup":
            self.printBanner()
            l = ArrudaCupHockeyLeague()
        else:
            print "ERROR: Unknown League '" + self.league + "'"
            return

        l.draftmode()

class StatTrackTest(unittest.TestCase):

    def testConstructor(self):
        s = StatTrack()
        self.assertEquals(s.getVersion(), str(StatTrack.StatTrackMajorVersion) + "." + str(StatTrack.StatTrackMinorVersion))
        print s.getFullVersionString()

if __name__ == '__main__':
    st = StatTrack()
    st.run()