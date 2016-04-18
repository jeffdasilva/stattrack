#!/usr/bin/env python

'''
@author: jdasilva
'''

import copy

from footballdb import FootballPlayerDB
from sitescraper.nfl.myfantasyleague import MyFantasyLeagueDotComScraper


db = FootballPlayerDB()
db.load()
#db.wget()

player_list = []
undo_stack = []
db_stack = []
autosave = True

while True:

    undo_operation = False
    cmd_accepted = False

    if autosave:
        db.save()

    cmd = raw_input('% ')

    if cmd == "undo":
        if len(undo_stack) == 0:
            print "Nothing to undo"
            continue
        else:
            undo_operation = True
            cmd = undo_stack.pop()
            print cmd

    if cmd == "autosave":
        autosave = not autosave

        if autosave:
            print "autosave is on"
        else:
            print "autosave is off"

        if not undo_operation:
            undo_stack.append("autosave")
        continue

    if cmd == "pop":
        if len(db_stack) == 0:
            print "Nothing to pop"
            continue
        else:
            db = db_stack.pop()
            print "Popping DB Stack to restore old state"

            if not undo_operation:
                undo_stack.append("push")

            continue
    elif cmd == "push":
        db_stack.append(copy.deepcopy(db))
        print "Pushing DB on stack"

        if not undo_operation:
            undo_stack.append("pop")

        continue

    cmdArr = cmd.split()

    if cmd == "":
        continue
    elif cmdArr[0] == "print":
        print ' '.join(cmdArr[1:])
        continue
    elif cmd == "exit" or cmd == "quit" or cmd == "q":
        break
    elif cmd == "update" or cmd == "wget":
        print "Updating Player Database from Web Info. Please Wait..."
        db_stack.append(copy.deepcopy(db))
        db.wget()

        mflSite = MyFantasyLeagueDotComScraper(43790,2016)
        mflSite.scrape()
        for p in mflSite.draftGrid:
            playerSearch = db.getRE(p['name'], position=p['position'], listDrafted=True, listIgnored=True)
            if playerSearch is None or len(playerSearch) == 0:
                print "ERROR: Player " + p['name'] + " is unknown. Skipping!"
            elif len(playerSearch) == 1:
                if not playerSearch[0].isDrafted:
                    print playerSearch[0].name + " was drafted by " + p['owner']
                    playerSearch[0].draft()
                playerSearch[0].update({'franchise':p['owner']})
            else:
                print "ERROR: Player " + p['name'] + " is ambiguous. Skipping!"
                for ply in playerSearch:
                    print " --> " + ply.name

        if not undo_operation:
            undo_stack.append("pop")
        continue

    elif cmdArr[0] == "save":
        print "Saving Player DB to Disk"
        db.save()

        if not undo_operation:
            undo_stack.append("print Can't undo save operation")

        continue
    elif cmdArr[0] == "load":
        print "Loading Player DB from Disk"
        db_stack.append(copy.deepcopy(db))
        db.load()

        if not undo_operation:
            undo_stack.append("pop")

        continue

    elif cmd == "list" or cmd == "ls":
        cmd_accepted = True

    elif cmdArr[0] == "ignore" or cmdArr[0] == "unignore":

        is_ignore_cmd = (cmdArr[0] == "ignore")

        tmp_player_list = player_list
        p_index = 0

        if len(cmdArr) > 1:
            if cmdArr[1].isdigit():
                p_index = int(cmdArr[1])
            else:
                tmp_player_list = db.get(' '.join(cmdArr[1:]), listIgnored=(not is_ignore_cmd))

                if len(tmp_player_list) != 1:
                    print "Can't " + cmdArr[0] + "! Command ARGS are too ambiguous"
                    continue

        if len(tmp_player_list) > 0:
            if p_index >= len(tmp_player_list):
                print "Can't " + cmdArr[0] + "! Player Index Arg exceeds number of players in Queue"
                continue
            else:

                if is_ignore_cmd:
                    p = tmp_player_list.pop(p_index)
                    p.ignore()
                else:
                    p = tmp_player_list[p_index]
                    p.unignore()
                print
                print p.name + " had been " + cmdArr[0] + "ed"
                print

                if not undo_operation:
                    if is_ignore_cmd:
                        undo_stack.append("unignore " + p.name)
                    else:
                        undo_stack.append("ignore " + p.name)

                continue
    elif cmdArr[0] == "draft" or cmdArr[0] == "d" or cmdArr[0] == "undraft":

        if cmdArr[0] == "d":
            cmdArr[0] = "draft"

        is_draft_cmd = (cmdArr[0] == "draft")

        tmp_player_list = player_list
        p_index = 0

        if len(cmdArr) > 1:
            if cmdArr[1].isdigit():
                p_index = int(cmdArr[1])
            else:
                tmp_player_list = db.get(' '.join(cmdArr[1:]), listDrafted=(not is_draft_cmd))

                if len(tmp_player_list) != 1:
                    print "Can't " + cmdArr[0] + "! Command ARGS are too ambiguous"
                    continue

        if len(tmp_player_list) > 0:
            if p_index >= len(tmp_player_list):
                print "Can't " + cmdArr[0] + "! Player Index Arg exceeds number of players in Queue"
                continue
            else:

                if is_draft_cmd:
                    p = tmp_player_list.pop(p_index)
                    #cost = raw_input(' --> for how much? ')
                    #if cost.isdigit():
                    #    cost = int(cost)
                    #else:
                    cost = 0
                    p.draft(cost)
                else:
                    p = tmp_player_list[p_index]
                    p.undraft()
                print
                print p.name + " had been " + cmdArr[0] + "ed"
                print

                if not undo_operation:
                    if is_draft_cmd:
                        undo_stack.append("undraft " + p.name)
                    else:
                        undo_stack.append("draft " + p.name)

                continue
        else:
            print "Can't Draft! No Players Queued Up Currently"
            continue
    elif cmd == "factory-reset":
        db_stack.append(db)
        db = FootballPlayerDB()
        db.wget()

        if not undo_operation:
            undo_stack.append("pop")

        continue
    elif cmd == "stats":
        print "Money Remaining: $" + str(db.moneyRemaining())
        print "Good Value Remaining: " + str(db.valueRemaining())
        print "Cost Per Value Unit: " + str(db.costPerValueUnit())
        continue

    if not cmd_accepted:
        for key in db.positionMap.keys():
            if cmdArr[0].lower() == key:
                player_list = db.get(position=key)
                cmd_accepted = True
                break

    if not cmd_accepted:
        if cmd.isdigit() and int(cmd) >= 0 and int(cmd) < len(player_list):
            player_list = [player_list[int(cmd)]]
        else:
            print "Searching for: " + cmd
            player_list_query = db.get(cmd)
            if len(player_list_query) == 0:
                print "No Players Found for search string: " + cmd
                continue
            player_list = player_list_query

    if len(player_list) == 0:
        print "Player Queue is Empty"
    else:

        cpv_mult = db.costPerValueUnit()

        for i, player in enumerate(player_list):
            if i >= 20:
                break
            #print '{0: >2}'.format(str(i)) + "  " + str(player) + " $" + str(player.value()*cpv_mult)
            print '{0: >2}'.format(str(i)) + "  " + str(player) + "  " + str(player.value())


if __name__ == '__main__':
    pass