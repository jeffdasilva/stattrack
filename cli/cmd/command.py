'''
Created on Sep 2, 2016

@author: jdasilva
'''
from abc import ABCMeta, abstractmethod
import unittest


##########################################################
# command (abstract base class)
class Command():
    __metaclass__ = ABCMeta

    def __init__(self, name):
        self.name = None

    @abstractmethod
    def help(self, args, parser): pass

    @abstractmethod
    def matches(self, cmd): pass

    @abstractmethod
    def apply(self, cmd, parser): pass

##########################################################

##########################################################
# error
class ErrorCommand(Command):

    def __init__(self):
        super(ErrorCommand, self).__init__('error')

    def help(self, args, parser):
        helpText = '''
assert an error
'''
        return helpText

    def matches(self):
        return False

    def apply(self, cmd, parser):
        from cli.parser import StatTrackParser
        response = "ERROR: " + cmd
        parser.status = StatTrackParser.StatusError
        return response
##########################################################

##########################################################
# help
class HelpCommand(Command):
    def __init__(self):
        super(ErrorCommand, self).__init__('help')

    def help(self, args, parser):
        helpText = '''
displays this help message
'''
        return helpText

    def matches(self):
        return False

    def apply(self, cmd, parser):
        from cli.parser import StatTrackParser
        response = "ERROR: " + cmd
        parser.status = StatTrackParser.StatusError
        return response

##########################################################


class TestCommands(unittest.TestCase):

    def testCommandIsAbstractClass(self):

        c = None
        try:
            c = Command('command')
        except TypeError:
            pass
            return

        self.assertNotEqual(c, None)
        self.assertTrue(False, "If you reach here then 'Command' is not an abstract class")



if __name__ == "__main__":
    unittest.main()