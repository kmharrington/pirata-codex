#!/usr/bin/env python3 

import pirata_codex as pc
import datetime as dt

discord = pc.Discord()
message = ''
try:
    message += pc.activity.look_for_no_raids(time_limit = dt.timedelta(7),
                                    exclude_list=['GYR0RRJ'])
except:
    discord.send('Activity Check failed\n'+message)
else:
    discord.send('Activity Check was successful\n' + message)

