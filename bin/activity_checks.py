#!/usr/bin/env python3 

import pirata_codex as pc
import datetime as dt

discord = pc.Discord()
message = ''
try:
    tracker = pc.activity.Activity_Tracker()
    message += tracker.check_war_participation()
    message += tracker.check_minimums()
except:
    discord.send('Activity Check failed\n'+message)
else:
    discord.send(message)
    
message = ''
try:
    message = tracker.congratulate(dt.datetime.now().weekday())
    if len(message)!=0:
        discord.announce(message)
except:
    discord.send('Congratuation Message Failed\n'+message)

    
