import datetime as dt
import dateutil.parser as dp
import requests
import json

class Clash():
    """class for communicating with Supercell"""

    def __init__(self, fname=None, clans_fname=None):
        """
        args: 
         fname - file name of sc_api json
         clans_fname - file name of json with list of relevant clans
        """
        if fname is None:
            fname = '/home/pi/pirata-codex/data/sc_api.json'
        with open(fname) as f:
            self.connect_info = json.load(f)

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


