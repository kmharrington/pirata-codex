import os
import numpy as np
import datetime as dt

import pirata_codex as pc
from pirata_codex.database import Clan, Clan_Data, Player, Player_Data

old_folder = '/home/pi/pirata-codex/old_data/'

"""
I want the database to be made, with clans added, but otherwise empty.
Or... I could do that all here
"""
pc.database.create_tables()
print('Tables Made')
pc.database_utils.verify_clan_table()
print('Populated Clan Table')

clan_map = {"pirates":"9RCRVL8V", "parallax":"2Y09LV28", "royals":"GYR0RRJ"}
session = pc.get_session()

for fname in sorted(os.listdir(old_folder)):
    if fname[-3:] != 'csv':
        continue
    clan, fdate = fname.split('.')[0].split('_')
    fdate = dt.datetime.strptime( fdate, '%Y%m%d') + dt.timedelta(hours=20)
    print('{} - {}'.format(clan, fdate))

    data = np.genfromtxt(old_folder+fname, delimiter=',', names=True, 
                         comments='$$$', dtype=None)
    entry = Clan_Data(clan_tag = clan_map[clan],
                      time = fdate,
                      num_members = len(data))
    session.add(entry)
    session.commit()

    for i in range(len(data)):
        #print(data['Name'][i].decode('utf-8'), 
        #        data['Tag'][i][1:].decode('utf-8'), 
        #        data['TH_Level'][i])
        name = data['Name'][i].decode('utf-8', "ignore")
        tag = data['Tag'][i][1:].decode('utf-8')
        q = session.query(Player)
        player = q.filter(Player.tag == tag).one_or_none()
        if player is None:
            print('Adding {} to database'.format(name))
            entry = Player( name = name,
                            tag = tag,
                            status = pc.ACTIVE,
                            current_clan_tag = None,
                            first_seen = fdate,
                            last_seen = fdate)
            session.add(entry)
        else:
            if fdate > player.last_seen:
                player.last_seen = fdate
        session.commit()

        entry = Player_Data(player_tag = tag,
                            time = fdate,
                            town_hall = int(data['TH_Level'][i]),
                            builder_hall = int(data['BH_Level'][i]),
                            xp = int(data['XP_Level'][i]),
                            best_trophies = int(data['Best_Trophies'][i]),
                            best_builder = int(data['Best_Versus_Trophies'][i]),
                            trophies = int(data['Current_Trophies'][i]),
                            trophies_builder = int(data['Builder_Hall_Trophies'][i]),
                            wins_attacks = None,
                            wins_defenses = None,
                            wins_builder = None,
                            barbarian_king = int(data['Barbarian_King'][i]),
                            archer_queen = int(data['Archer_Queen'][i]),
                            grand_warden = int(data['Grand_Warden'][i]),
                            battle_machine = int(data['Battle_Machine'][i]),
                            donates_total = int(data['Total_Donations'][i]), 
                            donates_spells = int(data['Total_Spells_Donated'][i]),
                            war_stars = int(data['Total_War_Stars'][i]),
                            gold_total = int(data['Total_Gold_Grab'][i]),
                            elixer_total = int(data['Total_Elixir_Grab'][i]),
                            de_total = int(data['Total_DE_Grab'][i]),
                            clan_games_xp = int(data['Clan_Games_XP'][i]))

        #print('Adding Data Entry for {} - {}'.format(entry.player_tag, entry.time))
        session.add(entry)
        session.commit()

session.close()
