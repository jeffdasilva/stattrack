#!/usr/bin/env python

'''
@author: jdasilva
'''
import unittest

from league.custom.oleague import OLeagueFootballLeague


class StatTrack():
    StatTrackMajorVersion = 0
    StatTrackMinorVersion = 5
    StatTrackBuildNumber = 9

    def __init__(self):
        pass

    def getVersion(self):
        return str(StatTrack.StatTrackMajorVersion) + "." + str(StatTrack.StatTrackMinorVersion)

    def getFullVersionString(self):
        return "[Version: " + self.getVersion() + ", Build: " + str(StatTrack.StatTrackBuildNumber) + "]"

    def printBanner(self):
        print "StatTrack\t" + self.getFullVersionString()
        print " https://github.com/jeffdasilva/stattrack"
        print
        print

    def run(self):
        self.printBanner()
        l = OLeagueFootballLeague()
        l.draftmode()

class StatTrackTest(unittest.TestCase):

    def testConstructor(self):
        s = StatTrack()
        self.assertEquals(s.getVersion(), str(StatTrack.StatTrackMajorVersion) + "." + str(StatTrack.StatTrackMinorVersion))
        print s.getFullVersionString()

if __name__ == '__main__':
    st = StatTrack()
    st.run()