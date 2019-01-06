#!/usr/bin/env python3

import pirata_codex as pc
import pirata_codex.database_utils as utils

discord = pc.Discord()
try:
    # Verify that I haven't added new clans to track.
    # Updates the Clan table
    utils.verify_clan_table()
    # Update the Clan_Data and Player tables
    message = utils.update_clan_data()
    # Look for missing people
    message += utils.flag_missing_players()
    # Update the Player_Data table
    message += utils.update_player_data()
    # Update the war status/list
    message += utils.update_war_list()
except:
    discord.send('Clash API pulls and/or Database update failed\n'+message)
else:
    discord.send(message)
