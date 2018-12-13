import os
import datetime as dt

from sqlalchemy import (Column, Integer, String, ForeignKey, Table, DateTime,
                    Boolean, Float)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

from pirata_codex.config import *
_Base = declarative_base()

class Clan(_Base):
    __tablename__ = 'Clan'

    tag = Column(String, primary_key = True)
    name = Column(String)

    data = relationship("Clan_Data",
                            back_populates="clan")


class Clan_Data(_Base):
    __tablename__ = 'Clan_Data'
    
    clan = relationship("Clan", back_populates="data")
    clan_tag = Column(String, ForeignKey('Clan.tag'), 
                        primary_key = True)

    time = Column(DateTime, primary_key = True)

    num_members = Column(Integer)
    war_wins = Column(Integer)
    war_losses = Column(Integer)
    war_ties = Column(Integer)

    @classmethod
    def from_json(cls, data, pull_time = None ):
        """
        Creates database entry from Supercell Clash json

        args:
            data - the json from the Supercell API
            pull_time - the time that data was acquired
        returns:
            Clan_Data entry
        """
        if pull_time is None:
            pull_time = dt.datetime.now()

        ## Deal with new clans with no war losses
        for k in ['warWins', 'warLosses', 'warTies']:
            if k not in data.keys():
                data[k] = 0
        
        return cls( clan_tag = data['tag'][1:],
                    time = pull_time,
                    num_members = data['members'],
                    war_wins = data['warWins'],
                    war_losses = data['warLosses'],
                    war_ties = data['warTies'] )

class Player(_Base):
    __tablename__ = 'Player'

    tag = Column(String, primary_key = True)
    name = Column(String)

    status = Column(Integer)
    current_clan_tag = Column(String)

    first_seen = Column(DateTime)
    last_seen = Column(DateTime)

    data = relationship("Player_Data",
                        back_populates='player')

    def town_hall(self):
        # Return players last seen town hall level
        if len(self.data) == 0:
            print('No data for player?')
            return np.nan
        return self.data[-1].town_hall
    
    def archer_queen(self):
        # Return players last seen AQ level
        if len(self.data) == 0:
            print('No data for player?')
            return np.nan
        return self.data[-1].archer_queen

    def barbarian_king(self):
        # Return players last seen BK level
        if len(self.data) == 0:
            print('No data for player?')
            return np.nan
        return self.data[-1].barbarian_king

    def grand_warden(self):
        # Return players last seen town hall level
        if len(self.data) == 0:
            print('No data for player?')
            return np.nan
        return self.data[-1].grand_warden

class Player_Data(_Base):
    __tablename__ = 'Player_Data'

    player = relationship("Player", back_populates='data')
    player_tag = Column(String, ForeignKey("Player.tag"),
                        primary_key=True)

    # General
    time = Column(String, primary_key=True)
    town_hall = Column(Integer)
    builder_hall = Column(Integer)
    xp = Column(Integer)

    # Trophies
    best_trophies = Column(Integer)
    best_builder = Column(Integer)
    trophies = Column(Integer)
    trophies_builder = Column(Integer)

    wins_attacks = Column(Integer)
    wins_defenses = Column(Integer)
    wins_builder = Column(Integer)

    # Heroes
    barbarian_king = Column(Integer)
    archer_queen = Column(Integer)
    grand_warden = Column(Integer)
    battle_machine = Column(Integer)

    # Donations
    donates_total = Column(Integer)
    donates_spells = Column(Integer)

    # Wars
    war_stars = Column(Integer)

    # Raiding
    gold_total = Column(Integer)
    elixer_total = Column(Integer)
    de_total = Column(Integer)
    clan_games_xp = Column(Integer)

    @classmethod
    def from_json(cls, data, pull_time = None):
        """
        Creates database entry from Supercell Clash (member) json

        args:
            data - the json from the Supercell API
            pull_time - the time that data was acquired
        returns:
            Clan_Data entry
        """
        if pull_time is None:
            pull_time = dt.datetime.now()
        bk, aq, gw, bm = 0, 0, 0, 0
        for hero in data['heroes']:
            if 'King' in hero['name']:
                bk = hero['level']
            elif 'Queen' in hero['name']:
                aq = hero['level']
            elif 'Warden' in hero['name']:
                gw = hero['level']
            elif 'Machine' in hero['name']:
                bm = hero['level']

        return cls( player_tag = data['tag'][1:],
                    time = pull_time,
                    town_hall = data['townHallLevel'],
                    builder_hall = data['builderHallLevel'],
                    xp = data['expLevel'],
                    best_trophies = data['bestTrophies'],
                    best_builder = data['bestVersusTrophies'],
                    trophies = data['trophies'],
                    trophies_builder = data['versusTrophies'],
                    wins_attacks = data['achievements'][12]['value'],
                    wins_defenses = data['achievements'][13]['value'],
                    wins_builder = data['achievements'][28]['value'],
                    barbarian_king = bk,
                    archer_queen = aq,
                    grand_warden = gw,
                    battle_machine = bm,
                    donates_total = data['achievements'][14]['value'],
                    donates_spells = data['achievements'][23]['value'],
                    war_stars = data['achievements'][20]['value'],
                    gold_total = data['achievements'][5]['value'],
                    elixer_total = data['achievements'][6]['value'],
                    de_total = data['achievements'][16]['value'],
                    clan_games_xp = data['achievements'][31]['value'],)


def get_engine():
    return create_engine('sqlite:///{}'.format(BASEDIR + configs['database']['db_name']))

def create_tables():
    engine = get_engine()
    _Base.metadata.create_all(engine)

def get_session(autoflush=False, multithread=False, **kwargs):
    return sessionmaker(bind=get_engine(), autoflush=autoflush, **kwargs)()

