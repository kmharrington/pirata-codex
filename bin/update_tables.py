import pirata_codex as pc
import pirata_codex.database_utils as utils

# Verify that I haven't added new clans to track.
# Updates the Clan table
utils.verify_clan_table()
# Update the Clan_Data and Player tables
utils.update_clan_data()
# Look for missing people
utils.flag_missing_players()
# Update the Player_Data table
utils.update_player_data()
