#!/usr/bin/env python3 

import pirata_codex as pc
import datetime as dt

discord = pc.Discord()
message = ''
try:
    tracker = pc.activity.Activity_Tracker()
    message += tracker.check_minimums()
except:
    discord.send('Activity Check failed\n'+message)
else:
    discord.send(message)

