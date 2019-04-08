import datetime as dt
import dateutil.parser as dp
import requests
import json
from pirata_codex.config import *

class Clash():
    """class for communicating with Supercell"""

    def __init__(self, clans_fname=None):
        """
        args: 
         fname - file name of sc_api json
         clans_fname - file name of json with list of relevant clans
        """
        self.connect_info = configs['clash']

        if clans_fname is None:
            fname = '/home/pi/pirata-codex/data/clans.json'
        with open(fname) as f:
            self.clan_list = json.load(f)['clans']

        self.header = {
                'Accept':'application/json',
                'Authorization':'Bearer ' + self.connect_info['token']
                }

    @staticmethod
    def convert_time(time_str):
        return dp.parse( time_str ).astimezone(tz=None).replace(tzinfo=None)
    
    def get_clan_data(self, clan_tag):
        """
        Retrieve SuperCell data about a clan
        args:
         clan_tag - the clan tag (without the #)
        raises:
         any connection related issues
        returns:
         json data from SuperCell
        """
        r = requests.get(self.connect_info['clans_url']+clan_tag, self.header)
        r.raise_for_status()
        return r.json()

    def get_clan_warlog(self, clan_tag):
        """
        Retrieve SuperCell data about a clan
        args:
         clan_tag - the clan tag (without the #)
        raises:
         any connection related issues
        returns:
         json data from SuperCell
        """
        r = requests.get(self.connect_info['clans_url']+clan_tag+'/warlog', self.header)
        r.raise_for_status()
        return r.json()

    def get_clan_war(self, clan_tag):
        """
        Retrieve SuperCell data about a clan
        args:
         clan_tag - the clan tag (without the #)
        raises:
         any connection related issues
        returns:
         json data from SuperCell
        """
        r = requests.get(self.connect_info['clans_url']+clan_tag+'/currentwar', self.header)
        r.raise_for_status()
        return r.json()
   
    def get_clan_cwl(self, clan_tag):
        """
        Retrieve SuperCell data about a CWL season
        args:
         clan_tag - the clan tag (without the #)
        raises:
         any connection related issues
        returns:
         json data from SuperCell
        """
        r = requests.get(self.connect_info['clans_url']+clan_tag+'/currentwar/leaguegroup', self.header)
        r.raise_for_status()
        return r.json()
        
    def get_clan_cwl_war(self, clan_tag):
        """
        Retrieve SuperCell data about a clan war
        args:
         clan_tag - the clan tag (without the #)
        raises:
         any connection related issues
        returns:
         json data from SuperCell
        """
        cwl = self.get_clan_cwl(clan_tag)
        if cwl['state'] != 'inWar':
            return 
        
        for day in cwl['rounds']:
            if day['warTags'][0] == '#0':
                continue
            for tag in day['warTags']:
                r = requests.get(self.connect_info['cwl_url']+tag[1:], self.header)
                cwl_war = r.json()
                if cwl_war['clan']['tag'][1:] == clan_tag or cwl_war['opponent']['tag'][1:] ==clan_tag:
                    if cwl_war['state'] != 'warEnded':
                        return cwl_war


    def get_player_data(self, player_tag):
        """
        Retrieve SuperCell data about a player
        args:
         player_tag - the player tag (without the #)
        raises:
         any connection related issues
        returns:
         json data from SuperCell
        """
        r = requests.get(self.connect_info['player_url']+player_tag,
                         self.header)
        r.raise_for_status()
        return r.json()


