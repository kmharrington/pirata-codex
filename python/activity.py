import numpy as np
import datetime as dt

from sqlalchemy import desc

import pirata_codex as pc
from pirata_codex.database import (Clan, Clan_Data, Player, Player_Data)
from pirata_codex.config import *

class Activity_Tracker:
    """
    class used to build up lists of player activity
    """
    def __init__(self):
        self.session = pc.get_session()
        self.configs = configs['activity']

        self.time_old = dt.datetime.now() - dt.timedelta(days = self.configs['time_limit'])
        self.time_new = dt.datetime.now() 
        self.time_tolerance = dt.timedelta(days=self.configs['time_tolerance'])
        print('Time limit {} and time tolerance {}'.format(self.time_old,
                                                        self.time_tolerance))
        self._get_active_players()
        print('Found {} active players'.format(len(self.active_list)))
        self.issues = []

    def _player_data_time(self, player, equality ):
        """
        return the Player_Data object before or after a specific time
        and within a specific tolerence

        args: 
            player - Player object
            equality - can be 'before' or 'after'
        returns:
            Player_Data object or None
        """
        assert (equality == 'before' or equality == 'after')

        pd = self.session.query(Player_Data).filter(Player_Data.player_tag == player.tag)
        if equality == 'before':
            #print('Looking between {} and {}'.format(self.time_old - self.time_tolerance,
            #                                        self.time_old))
            pd = pd.filter(Player_Data.time <= self.time_old,
                           Player_Data.time >= self.time_old - self.time_tolerance)
            pd = pd.order_by( desc(Player_Data.time) ).first()
        else:
            pd = pd.filter(Player_Data.time <= self.time_new,
                           Player_Data.time >= self.time_new - self.time_tolerance)
            pd = pd.order_by( Player_Data.time ).first()
        return pd

    def _get_active_players(self):
        """
        creates a list of active players last seen within the time tolerance
        
        args:
            none
        returns:
            nones
        """
        self.active_list = self.session.query(Player).filter(Player.status == pc.ACTIVE,
                          Player.last_seen >= dt.datetime.now()-self.time_tolerance).all()

    def add_issue(self, player, reason, value):
        print('Found an issues with {}'.format(player.name))
        for issue in self.issues:
            if issue[0].tag == player.tag:
                issue[1].append(reason)
                issue[2].append(value)
                return
        self.issues.append( (player, [reason], [value]) )

    def look_for_no_raids(self):
        """
        Look for members with no raids in the last week and adds to the issue list

        args:
            None
        returns:
            None
        """

        for player in self.active_list:
            p0 = self._player_data_time(player, 'before')
            if p0 is None:
                continue
            p1 = self._player_data_time(player, 'after')
            #print( p0.payer_tag, p0.gold_total )
            if p1 is None:
                # I want this to cause fails so I know if my bot or database has issues
                raise ValueError('no recent enough player data for {}'.format(player.name))
            #print( p0.player_tag, p0.gold_total, p1.gold_total)
            if (p0.gold_total == p1.gold_total and p0.elixer_total == p1.elixer_total
                    and p0.de_total == p1.de_total):
                self.add_issue( player, 'no raids', 0)

    def look_for_low_donates(self):
        """
        Look for members who were low on donations and adds to the issue list

        args:
            None
        returns:
            None
        """
    
        for player in self.active_list:
            p0 = self._player_data_time(player, 'before')
            p1 = self._player_data_time(player, 'after')
            
            if p0 is None or p1 is None:
                continue
            
            if p1.donates_total - p0.donates_total <= self.configs['min_donates']:
               self.add_issue( player, 'low donations', 
                               p1.donates_total - p0.donates_total)

#def check_donations( player_list, donate_min, time_limit=dt.timedelta(7),
#                        t1=dt.datetime.now(), old_limit=dt.timedelta(1) ):



if __name__ == "__main__":
    tracker = Activity_Tracker()
    tracker.look_for_no_raids()
    tracker.look_for_low_donates()


