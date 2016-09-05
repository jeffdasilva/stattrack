'''
Created on Sep 2, 2016

@author: jdasilva
'''
from abc import ABCMeta, abstractmethod
import copy
import unittest


##########################################################
# command (abstract base class)
class Command():
    __metaclass__ = ABCMeta

    GenericCommands = []

    def __init__(self, name):
        self.name = name
        self.aliases = []
        self.hidden = False

    @abstractmethod
    def help(self, args, parser): pass

    def extendedHelp(self, args, parser):
        return "No further info for command " + self.name

    def getCmdKeyWord(self, cmd):
        return cmd.split(' ',1)[0].lower()

    def getCmdArgs(self, cmd):
        cmdKeyWord = self.getCmdKeyWord(cmd)

        cmdHasKeyWord = False
        if cmdKeyWord == self.name.lower():
            cmdHasKeyWord = True
        if not cmdHasKeyWord:
            for alias in self.aliases:
                if cmdKeyWord == alias.lower():
                    cmdHasKeyWord = True

        if cmdHasKeyWord and cmd.lower().startswith(cmdKeyWord):
            return cmd.lower()[len(cmdKeyWord):].lstrip()
        else:
            return cmd

    def matches(self, cmd):

        if self.name == None:
            return False

        cmdKeyWord = self.getCmdKeyWord(cmd)

        if cmdKeyWord.lower() == self.name.lower():
            return True

        for alias in self.aliases:
            if alias.lower() == cmdKeyWord.lower():
                return True

        return False

    def preApplyMessage(self, cmd, parser):
        return None

    @abstractmethod
    def apply(self, cmd, parser): pass

    def statusTrue(self, parser):
        from cli.parser import StatTrackParser
        parser.status = StatTrackParser.StatusTrue
        return parser.status

    def statusFalse(self, parser):
        from cli.parser import StatTrackParser
        parser.status = StatTrackParser.StatusFalse
        return parser.status

    def statusError(self, parser):
        from cli.parser import StatTrackParser
        parser.status = StatTrackParser.StatusError
        return parser.status

    def statusExit(self, parser):
        from cli.parser import StatTrackParser
        parser.status = StatTrackParser.StatusExit
        return parser.status

    def isCurrentStatusTrue(self, parser):
        from cli.parser import StatTrackParser
        return parser.status == StatTrackParser.StatusTrue

    def getLeague(self, parser):
        self.statusTrue(parser)
        if parser.league is None:
            return parser.error("Nothing to "+ self.name +". The League is not configured")
        return parser.league

    def getDB(self, parser):
        self.statusTrue(parser)
        leagueOrResponseError = self.getLeague(parser)
        if not self.isCurrentStatusTrue(parser):
            response = leagueOrResponseError
            return response

        league = leagueOrResponseError

        if league.db is None:
            return parser.error("Nothing to " + self.name + ". The League's database is not configured")

        return league.db

    def getPlayer(self, playerArg, parser,listDrafted=False,listIgnored=False):

        dbOrResponse = self.getDB(parser)
        if not self.isCurrentStatusTrue(parser):
            response = dbOrResponse
            return response

        db = dbOrResponse

        if playerArg == "":

            if len(parser.player_list) == 0:
                return parser.error("Can't " + self.name + "! No players in player queue")
            player = parser.player_list.pop(0)

        elif playerArg.isdigit():
            index = int(playerArg)

            if index >= len(parser.player_list):
                return parser.error("Can't " + self.name + "! Player index argument exceeds number of players in player queue")

            player = parser.player_list.pop(index)

        else:
            player_list = db.get(playerArg, listDrafted=listDrafted, listIgnored=listIgnored)

            if len(player_list) != 1:
                return parser.error("Can't " + self.name + " " + playerArg + "! Command ARGS are too ambiguous")

            player = player_list.pop(0)

            if player in parser.player_list:
                parser.player_list.remove(player)

        return player


##########################################################

##########################################################
# error
class ErrorCommand(Command):

    def __init__(self):
        super(ErrorCommand, self).__init__('error')
        self.hidden = True

    def help(self, args, parser):
        return "Assert an error"

    def apply(self, cmd, parser):
        response = "ERROR: " + cmd
        self.statusError(parser)
        return response

Command.GenericCommands.append(ErrorCommand())
##########################################################

##########################################################
# blank
class BlankCommand(Command):

    def __init__(self):
        super(BlankCommand, self).__init__('blank')
        self.hidden = True
        self.aliases.append('')

    def help(self, args, parser):
        return "Do nothing"

    def apply(self, cmd, parser):
        self.statusTrue(parser)
        return ""

Command.GenericCommands.append(BlankCommand())
##########################################################

##########################################################
# help
class HelpCommand(Command):
    def __init__(self):
        super(HelpCommand, self).__init__('help')

    def help(self, args, parser):
        return "Display this help message"

    def apply(self, cmd, parser):

        response = "\n" + parser.bold("COMMANDS") + "\n\n"
        response += '{0: >15}'.format("<command>") + ":  " + "<description>" + "\n\n"

        for cmd in sorted(parser.commands, key=lambda c: c.name):
            if cmd.hidden:
                continue
            response += '{0: >15}'.format(cmd.name) + ":  " + cmd.help(cmd, parser) + "\n"

        response += "\n" + parser.bold("AUTHOR") + "\n\tWritten by Jeff DaSilva.\n"

        self.statusTrue(parser)
        return response

Command.GenericCommands.append(HelpCommand())
##########################################################

##########################################################
# undo
class UndoCommand(Command):
    def __init__(self):
        super(UndoCommand, self).__init__('undo')

    def help(self, args, parser):
        return "Undo the last command"

    def apply(self, cmd, parser):

        if len(parser.undo_stack) == 0:
            return parser.error("Nothing to undo")

        parser.undoMode = True
        cmd = parser.undo_stack.pop()
        response = parser.processCommand(cmd)
        parser.undoMode = False

        return response

Command.GenericCommands.append(UndoCommand())
##########################################################

##########################################################
# autosave
class AutoSaveCommand(Command):
    def __init__(self):
        super(AutoSaveCommand, self).__init__('autosave')

    def help(self, args, parser):
        helpText = "Toggle autosave "
        if parser.autosave:
            helpText += "off [autosave is currently enabled]"
        else:
            helpText += "on [autosave is currently disabled]"
        return helpText

    def apply(self, cmd, parser):

        parser.autosave = not parser.autosave
        if parser.autosave:
            response = "autosave is on"
        else:
            response = "autosave is off"

        parser.pushOnUndoStack("autosave")

        self.statusTrue(parser)
        return response

Command.GenericCommands.append(AutoSaveCommand())
##########################################################

##########################################################
# pop
class PopCommand(Command):
    def __init__(self):
        super(PopCommand, self).__init__('pop')

    def help(self, args, parser):
        return "Pop previously pushed saved player database off the stack"

    def apply(self, cmd, parser):

        if len(parser.db_stack) == 0:
            return parser.error("Nothing to pop")

        leagueOrResponse = self.getLeague(parser)
        if not self.isCurrentStatusTrue(parser):
            response = leagueOrResponse
            return response

        league = leagueOrResponse

        league.db = parser.db_stack.pop()
        response = "Popping player database stack to restore old state"

        parser.pushOnUndoStack("push")

        self.statusTrue(parser)

        return response

Command.GenericCommands.append(PopCommand())
##########################################################

##########################################################
# push
class PushCommand(Command):
    def __init__(self):
        super(PushCommand, self).__init__('push')

    def help(self, args, parser):
        return "Push current player database to the stack to temporarily save it. Restore it later with pop command"

    def apply(self, cmd, parser):

        dbOrResponse = self.getDB(parser)
        if not self.isCurrentStatusTrue(parser):
            response = dbOrResponse
            return response

        db = dbOrResponse

        parser.db_stack.append(copy.deepcopy(db))
        response = "Pushing current player database onto the stack to save current state"

        parser.pushOnUndoStack("pop")

        self.statusTrue(parser)

        return response

Command.GenericCommands.append(PushCommand())
##########################################################

##########################################################
# print
class PrintCommand(Command):
    def __init__(self):
        super(PrintCommand, self).__init__('print')
        self.aliases.append("echo")

    def help(self, args, parser):
        return "Echo a line of text"

    def apply(self, cmd, parser):
        self.statusTrue(parser)
        return self.getCmdArgs(cmd)

Command.GenericCommands.append(PrintCommand())
##########################################################

##########################################################
# quit
class QuitCommand(Command):
    def __init__(self):
        super(QuitCommand, self).__init__('quit')
        self.aliases.append("exit")
        self.aliases.append("q")

    def help(self, args, parser):
        return "Exit this program"

    def apply(self, cmd, parser):
        self.statusExit(parser)
        return "Goodbye Cruel World"

Command.GenericCommands.append(QuitCommand())
##########################################################

##########################################################
# update
class UpdateCommand(Command):
    def __init__(self):
        super(UpdateCommand, self).__init__('update')

    def help(self, args, parser):
        return "Update player database by web scraping applicable web sites"

    def preApplyMessage(self, cmd, parser):
        return "Updating Player Database from Web. Please Wait..."

    def apply(self, cmd, parser):

        dbOrResponse = self.getDB(parser)
        if not self.isCurrentStatusTrue(parser):
            response = dbOrResponse
            return response

        db = dbOrResponse

        parser.pushState()
        db.wget()
        response = "Player Database Updated"
        self.statusTrue(parser)

        return response

Command.GenericCommands.append(UpdateCommand())
##########################################################

##########################################################
# save
class SaveCommand(Command):
    def __init__(self):
        super(SaveCommand, self).__init__('save')

    def help(self, args, parser):
        return "Save player database to disk"

    def preApplyMessage(self, cmd, parser):
        return "Saving player database to disk..."

    def apply(self, cmd, parser):

        dbOrResponse = self.getDB(parser)
        if not self.isCurrentStatusTrue(parser):
            response = dbOrResponse
            return response

        db = dbOrResponse

        db.save()
        response = "Player database saved"
        self.statusTrue(parser)

        parser.pushOnUndoStack("print Can't undo save operation")

        return response

Command.GenericCommands.append(SaveCommand())
##########################################################

##########################################################
# load
class LoadCommand(Command):
    def __init__(self):
        super(LoadCommand, self).__init__('load')

    def help(self, args, parser):
        return "Load player database from disk"

    def preApplyMessage(self, cmd, parser):
        return "Loading player database from disk..."

    def apply(self, cmd, parser):

        dbOrResponse = self.getDB(parser)
        if not self.isCurrentStatusTrue(parser):
            response = dbOrResponse
            return response

        db = dbOrResponse

        parser.pushState()
        db.load()

        response = "Player database loaded"
        self.statusTrue(parser)

        return response

Command.GenericCommands.append(LoadCommand())
##########################################################

##########################################################
# list
class ListCommand(Command):
    def __init__(self):
        super(ListCommand, self).__init__('list')
        self.aliases.append("ls")

    def help(self, args, parser):
        return "List all players currently in your player queue"

    def apply(self, cmd, parser):

        if len(parser.player_list) == 0:
            response = "Player Queue is Empty"
            self.statusFalse(parser)
        else:
            response = "---------------------------------------------------------------------\n"
            for i, player in enumerate(parser.player_list):
                if i >= 25:
                    break

                response += '{0: >2}'.format(str(i)) + "  "
                response += player.name
                response += "\n"

            response += "---------------------------------------------------------------------\n"

            self.statusTrue(parser)
        return response

Command.GenericCommands.append(ListCommand())
##########################################################

##########################################################
# search
class SearchCommand(Command):
    def __init__(self):
        super(SearchCommand, self).__init__('search')

    def help(self, args, parser):
        return "Search player database with a player name and add results to player queue"

    def apply(self, cmd, parser):

        dbOrResponse = self.getDB(parser)
        if not self.isCurrentStatusTrue(parser):
            response = dbOrResponse
            return response

        db = dbOrResponse

        player_list_query = db.get(self.getCmdArgs(cmd))
        parser.player_list = player_list_query
        if len(player_list_query) == 0:
            response = "No players found for search string: " + self.getCmdArgs(cmd)
            self.statusFalse(parser)
        else:
            response = ListCommand().apply("list", parser)

        return response

Command.GenericCommands.append(SearchCommand())
##########################################################

##########################################################
# draft
class DraftCommand(Command):
    def __init__(self):
        super(DraftCommand, self).__init__('draft')
        self.aliases.append("d")

    def help(self, args, parser):
        return "Draft a player"

    def apply(self, cmd, parser):

        playerOrResponse = self.getPlayer(self.getCmdArgs(cmd), parser)
        if not self.isCurrentStatusTrue(parser):
            response = playerOrResponse
            return response

        player = playerOrResponse

        player.draft()
        response = player.name + " has been " + self.name + "ed"
        parser.pushOnUndoStack("undraft " + player.name)

        return response

Command.GenericCommands.append(DraftCommand())
##########################################################

##########################################################
# undraft
class UndraftCommand(Command):
    def __init__(self):
        super(UndraftCommand, self).__init__('undraft')

    def help(self, args, parser):
        return "Undraft a player"

    def apply(self, cmd, parser):

        playerOrResponse = self.getPlayer(self.getCmdArgs(cmd), parser, listDrafted=True)
        if not self.isCurrentStatusTrue(parser):
            response = playerOrResponse
            return response

        player = playerOrResponse

        player.undraft()
        response = player.name + " has been " + self.name + "ed"
        parser.pushOnUndoStack("undraft " + player.name)

        return response

Command.GenericCommands.append(UndraftCommand())
##########################################################

##########################################################
# ignore
class IgnoreCommand(Command):
    def __init__(self):
        super(IgnoreCommand, self).__init__('ignore')

    def help(self, args, parser):
        return "Ignore a player so that they never appear in your player queue"

    def apply(self, cmd, parser):

        playerOrResponse = self.getPlayer(self.getCmdArgs(cmd), parser)
        if not self.isCurrentStatusTrue(parser):
            response = playerOrResponse
            return response

        player = playerOrResponse

        player.ignore()
        response = player.name + " has been " + self.name + "ed"
        parser.pushOnUndoStack("unignore " + player.name)

        return response

Command.GenericCommands.append(IgnoreCommand())
##########################################################


##########################################################
# unignore
class UnignoreCommand(Command):
    def __init__(self):
        super(UnignoreCommand, self).__init__('unignore')

    def help(self, args, parser):
        return "Stop ignoring a player you've previously ignored using the ignore command"

    def apply(self, cmd, parser):

        playerOrResponse = self.getPlayer(self.getCmdArgs(cmd), parser, listIgnored=True)
        if not self.isCurrentStatusTrue(parser):
            response = playerOrResponse
            return response

        player = playerOrResponse

        player.unignore()
        response = player.name + " has been " + self.name + "ed"
        parser.pushOnUndoStack("ignore " + player.name)

        return response

Command.GenericCommands.append(UnignoreCommand())
##########################################################

##########################################################
# ToDo Commands:
# position (example: qb,rb,wr,def,k,etc)
# info
# factor-reset
# draft specific stuff for auction draft
# mfl specific scraper stuff for update command
# stats
# list commands needs custom formatting
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

    def testHelp(self):
        from cli.parser import StatTrackParser
        p = StatTrackParser(None)
        p.commands = [ HelpCommand() ]
        p.processCommandAndResponse("help")
        self.assertNotEqual(p.status, StatTrackParser.StatusError)

    def testPrint(self):
        from cli.parser import StatTrackParser
        pcmd = PrintCommand()
        self.assertTrue(pcmd.matches("print foo"))
        self.assertTrue(pcmd.matches("echo foo"))
        self.assertEquals(pcmd.apply("print foo bar",StatTrackParser(None)),"foo bar")
        self.assertEquals(pcmd.apply("echo foo bar",StatTrackParser(None)),"foo bar")
        self.assertEquals(pcmd.apply("foo bar",StatTrackParser(None)),"foo bar")
        self.assertEquals(pcmd.apply("echo echo foo bar",StatTrackParser(None)),"echo foo bar")


if __name__ == "__main__":
    unittest.main()
