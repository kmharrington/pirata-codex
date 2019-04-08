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
        self._build_player_list()
        print('Found {} active players'.format(len(self.player_list)))
        self.issues = []
    
    @property
    def activity_array(self):
        if not hasattr(self, '_activity_array'):
            self.create_activity_array()
        return self._activity_array
    
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
            pd = pd.filter(Player_Data.time <= self.time_old,
                           Player_Data.time >= self.time_old - self.time_tolerance)
            pd = pd.order_by( desc(Player_Data.time) ).first()
        else:
            pd = pd.filter(Player_Data.time <= self.time_new,
                           Player_Data.time >= self.time_new - self.time_tolerance)
            pd = pd.order_by( Player_Data.time ).first()
        return pd

    def _build_player_list(self):
        """
        create a list of tuples which are [(player, p0, p1)] to calculate activity
        flags off of

        args:
            none
        returns:
            none
        """

        active_list = self.session.query(Player).filter(Player.status == pc.ACTIVE,
                          Player.last_seen >= dt.datetime.now()-self.time_tolerance).all()
        self.player_list = []
        for player in active_list:
            p0 = self._player_data_time(player, 'before')
            if p0 is None:
                p0 = None
            p1 = self._player_data_time(player, 'after')
            #print( p0.payer_tag, p0.gold_total )
            if p1 is None:
                # I want this to cause fails so I know if my bot or database has issues
                raise ValueError('no recent enough player data for {}'.format(player.name))
            self.player_list.append( [player, p0, p1] )

    def calc_war_count(self):
        """
        calculates and returns the number of wars each player has been in
        matched to the player list
        """
        wars = np.zeros( (len(self.player_list),) )
        for p, (player, p0, p1) in enumerate(self.player_list):
            if p0 is None:
                wars[p] = np.nan
                continue
            q = self.session.query(Player_Data).filter(Player_Data.player_tag == player.tag)
            q = q.filter( Player_Data.time >= p0.datetime() - self.time_tolerance/2.0,
                          Player_Data.time <= p1.datetime() + self.time_tolerance/2.0,
                          Player_Data.in_war,
                          Player_Data.war_state != ENDED).all()
            if len(q) == 0:
                wars[p] = 0
                continue
            opponents = [md.war_opponent for md in q]
            wars[p] = len( np.unique(opponents) )
        return wars

    def calc_resource_grab(self):
        """
        calculates a returns the resources raided by each player matched
        to the player list

        args:
            None
        returns:
            list of resources grabbed
        """
        resources = np.zeros( (len(self.player_list),) )
        for p,(player, p0, p1) in enumerate(self.player_list):
            if p0 is None:
                resources[p] = np.nan
                continue
            resources[p] = p1.gold_total - p0.gold_total + \
                            p1.elixer_total - p0.elixer_total + \
                            p1.de_total - p0.de_total
        return resources

    def calc_donates(self):
        """
        calculate the total donations for everyone

        args:
            None
        returns:
            list of donations
        """
        donates = np.zeros( (len(self.player_list),) )
        for p,(player, p0, p1) in enumerate(self.player_list):
            if p0 is None:
                print(player.name +'is new') 
                donates[p] = np.nan
                continue
            donates[p] = p1.donates_total - p0.donates_total
        return donates


    def calc_clan_games(self):
        """
        calculate the clan games XP for everyone

        args:
            None
        returns:
            list of clan game xp
        """
        cg_xp = np.zeros( (len(self.player_list),) )
        for p,(player, p0, p1) in enumerate(self.player_list):
            if p0 is None:
                cg_xp[p] = np.nan
                continue
            cg_xp[p] = p1.clan_games_xp - p0.clan_games_xp
        return cg_xp

    def calc_war_stars(self):
        """
        calculate the total war stars for everyone

        args:
            None
        returns:
            list of war stars
        """
        war_stars = np.zeros( (len(self.player_list),) )
        for p,(player, p0, p1) in enumerate(self.player_list):
            if p0 is None:
                war_stars[p] = np.nan
                continue
            war_stars[p] = p1.war_stars - p0.war_stars
        return war_stars

    def create_activity_array(self):
        array = np.zeros( len(self.player_list), 
                    dtype = [('names', 'S30'),
                             ('tag', 'S30'), ('clan_tag', 'S30'),
                             ('donates', np.float),
                             ('war_stars', np.float),
                             ('war_count', np.float),
                             ('clan_games', np.float),
                             ('resources', np.float),
                             ('barbarian_king', np.int32),
                             ('archer_queen', np.int32),
                             ('grand_warden', np.int32),
                             ('total_heroes', np.int32),
                             ('town_hall', np.int32)])
        array['names'] = [ removeNonAscii(p[0].name) for p in self.player_list]
        array['tag'] = [p[0].tag for p in self.player_list]
        array['town_hall'] = [p[0].town_hall() for p in self.player_list]
        array['barbarian_king'] = [p[0].barbarian_king() for p in self.player_list]
        array['archer_queen'] = [p[0].archer_queen() for p in self.player_list]
        array['grand_warden'] = [p[0].grand_warden() for p in self.player_list]
        array['total_heroes'] = [p[0].barbarian_king() +
                                 p[0].archer_queen() +
                                 p[0].grand_warden() for p in self.player_list]
        array['clan_tag'] = [p[0].current_clan_tag for p in self.player_list]
        array['donates'] = self.calc_donates()
        array['clan_games'] = self.calc_clan_games()
        array['war_stars'] = self.calc_war_stars()
        array['war_count'] = self.calc_war_count()
        array['resources'] = self.calc_resource_grab()
        
        self._activity_array = array

    def check_minimums(self):
        if not 'min_donates' in self.configs.keys():
            print('No minimum donations in config file')
            self.configs['min_donates'] = np.inf
        if not 'min_war_stars' in self.configs.keys():
            print('No minimum war stars in configs')
            self.configs['min_war_stars'] = np.inf
        if not 'min_clan_games' in self.configs.keys():
            print('No minimum clan games in configs')
            self.configs['min_clan_games'] = np.inf
        if not 'min_resources' in self.configs.keys():
            print('No minimum resources in configs')
            self.configs['min_resources'] = np.inf
        if not 'min_war_count' in self.configs.keys():
            print('No minimum war count in configs')
            self.configs['min_war_count'] = np.inf
        
        msk = np.all([self.activity_array['donates'] < self.configs['min_donates'],
                      self.activity_array['war_stars'] < self.configs['min_war_stars'],
                      self.activity_array['clan_games'] < self.configs['min_clan_games'],
                      self.activity_array['resources'] < self.configs['min_resources'],
                      self.activity_array['war_count'] < self.configs['min_war_count']],axis=0)
        msk[np.isnan(self.activity_array['donates'])] = False
        
        failed = np.sort( self.activity_array[msk], order='resources')
        message = '----------------\n'
        if len(failed) > 0:
            message += 'Between {} and {}\n'.format(self.time_old, self.time_new) 
            message += '----------------\n'
        for i in range(len(failed)):
            if failed['tag'][i].decode('utf-8') in self.configs['exclude_list']['players']:
                continue
            if failed['clan_tag'][i].decode('utf-8') in self.configs['exclude_list']['clans']:
                continue
            
            message += '{} missed activity requirements\n'.format(
                                                    failed['names'][i].decode('utf-8'))
            message += '\t{} donations,\t{} war stars,'.format(failed['donates'][i],
                                                                failed['war_stars'][i])
            message += '\t{} clan games\n'.format(failed['clan_games'][i])
            message += '\tCollected {} in resources\n'.format(failed['resources'][i])
            message += '----------------\n'
        return message

    def check_war_participation(self):
        message = '----------------\n'
        for player, p0, p1 in self.player_list:
            if len(player.data) < 18:
                continue
            for data in player.data[-18:][::-1]:
                if data.war_opponent is not None:
                    break
            if data.datetime() < dt.datetime.now() - dt.timedelta(days=14):

                if player.tag in self.configs['exclude_list']['players']:
                        continue
                if player.current_clan_tag in self.configs['exclude_list']['clans']:
                    continue

                message += "{}'s last war was at least {} days ago\n".format(player.name, 
                                                          (dt.datetime.now()-data.datetime()).days)
        return message
    
    def congratulate(self, day_of_week=None):
        message = ''
        if day_of_week is None or day_of_week == 6:
            alist = np.sort(self.activity_array, order=['donates','resources'])[::-1]
            msk = ~np.isnan(alist['donates'])
            message += "Let's Congratulate our Top 10 Donators for the Week!```"
            for i in range(10):
                message += '{:2d}. {:15}: {}\n'.format(i+1, alist['names'][msk][i].decode('utf-8'), alist['donates'][msk][i])
            message += '```'
        return message
    
def removeNonAscii(s): 
    return "".join(i for i in s if ord(i)<128)

if __name__ == "__main__":
    tracker = Activity_Tracker()
    #print( tracker.calc_resource_grab() )
    #print( tracker.calc_donates() )
    #print( tracker.calc_clan_games() )
    #print( tracker.calc_war_stars() )
    tracker.check_minimums()
    #tracker.look_for_low_donates()


