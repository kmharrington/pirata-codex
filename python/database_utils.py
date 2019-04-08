import os
import json
import logging
import datetime as dt
import numpy as np

from sqlalchemy import and_, or_, not_

from pirata_codex import get_session, Clan, Clan_Data, Player, Player_Data
from pirata_codex.config import *
from pirata_codex.clash import Clash

formater = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
db_logger = logging.getLogger('database')
db_logger.setLevel(logging.INFO)

# I will want this later for file logging
#fileHandler = logging.FileHandler("{0}/{1}.log".format(logPath, fileName))
#fileHandler.setFormatter(logFormatter)
#rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formater)
db_logger.addHandler(consoleHandler)

def verify_clan_table( ):
    """ 
    Verifies that all the clans in data/clans.json are in the database
    Adds clans to the table if missing

    args:
        absolute file path of clans.json
    returns:
        nothing
    """
    
    clan_list = configs['clans']
    
    clan_list.append( {"name":"Gone","tag":"00000000"} )
    session = get_session()

    for clan in clan_list:
        q = session.query(Clan).filter(Clan.tag == clan['tag'],
                                        Clan.name == clan['name'])
        if q.count() == 0:
            db_logger.info('{} not found, adding to table'.format(clan['name']))
            db_clan = Clan(tag = clan['tag'], 
                            name= clan['name'],)
            session.add(db_clan)
            session.commit()
        elif q.count() == 1:
            db_logger.debug('{} in database, skipping'.format(clan['name']))
            continue
        else:
            db_logger.critical('{} is in the database twice?'.format(clan['name']))
            continue
    session.close()
    db_logger.debug('Clan Table Updated')

def update_clan_data(update_players=True):
    """
    Goes through the clan table and creates clan data for each clan

    args:
        update_players - if True the player table to is updated to add new 
                    players and the time they were last seen in one of our
                    clans
    returns:
        message to post on discord
    """

    session = get_session()
    clan_list = session.query(Clan).all()
    clash = Clash()
    
    message = ''

    for clan in clan_list:
        if clan.tag == "00000000":
            continue
        pull_time = dt.datetime.now()
        data = clash.get_clan_data( clan.tag )
        db_logger.debug('Pulled data from {}'.format(clan.name))
        
        entry = Clan_Data.from_json(data, pull_time)
        db_logger.debug('Adding {} with {} members'.format(entry.clan_tag, entry.num_members))
        session.add(entry)
        session.commit()
        if not update_players:
            continue
        
        for mem_data in data['memberList']:
            member = session.query(Player).filter(Player.tag == mem_data['tag'][1:]).one_or_none()
            if member is None:
                member = Player(tag = mem_data['tag'][1:],
                                name = mem_data['name'],
                                status = ACTIVE,
                                current_clan_tag = data['tag'][1:],
                                first_seen = pull_time,
                                last_seen = pull_time)
                db_logger.info('Adding new member {}'.format(member.name))
                message += 'Found New Member - {}\n'.format(member.name)
                session.add(member)
                session.commit()
            else:
                if member.status == INACTIVE:
                    message += 'Found previous member - {}!\n'.format(member.name)
                    member.status = ACTIVE
                    session.commit()
                db_logger.debug('Found {} again'.format(member.name))
                member.last_seen = pull_time
                member.current_clan_tag = clan.tag
                if member.name != mem_data['name']:
                    db_logger.info('{} changed their name to {}'.format(member.name,
                                                                        mem_data['name']))
                    message += '*{}* changed their name to *{}*\n'.format(member.name,
                                                                mem_data['name'])
                    member.name = mem_data['name']
                
                session.commit()
    session.close()
    return message
    

def flag_missing_players( time_limit=5 ):
    """
    Sets players who haven't been seen in a period of time as inactive

    args:
        time_limit - the number of days a player hasn't been seen to consider
                    them inactive
    returns:
        message to post on discord
    """
    message = ''
    session = get_session()
    inactives = session.query(Player).filter( Player.last_seen <= dt.datetime.now()-
                                        dt.timedelta(days=time_limit),
                                        Player.status == ACTIVE).all() 
    db_logger.info('{} players are missing'.format(len(inactives)))
    for mem in inactives:
        mem.status = INACTIVE
        message += '{} has left the clans\n'.format(mem.name)
    session.commit()
    session.close()
    return message

def update_player_data():
    """
    Pull activity data from all players listed as ACTIVE within Pirates

    returns:
        message to post on discord
    """
    
    session = get_session()
    members = session.query(Player).filter(Player.status==ACTIVE).all()
    db_logger.info('Updating {} players in the pirate family'.format(len(members)))
    message = 'Updated info for the {} active members\n'.format(len(members))
    clash = Clash()

    for member in members:
        mem_data = clash.get_player_data(member.tag)
        pull_time = dt.datetime.now()
        entry = Player_Data.from_json(mem_data, pull_time)
        db_logger.debug('Adding Entry for {} from {}'.format(entry.player_tag, entry.time))
        session.add(entry)
        if "clan" in mem_data.keys():
            member.current_clan_tag = mem_data['clan']['tag'][1:]
        else:
            member.current_clan_tag = "00000000"
        session.commit()
    session.close()
    return message
    
def update_war_list():
    '''
    Check each clan for wars, update war info clan data and
    in player data
    '''

    session = get_session()
    clan_list = session.query(Clan).all()
    clash = Clash()
    
    message = ''

    for clan in clan_list:
        if clan.tag == "00000000":
            continue
        
        cd = clan.data[-1]
        
        war = clash.get_clan_war(clan.tag)
        ## Add exception for when war isn't there
        if 'state' in war.keys() and war['state'] == 'notInWar':
            war = clash.get_clan_cwl_war(clan.tag)
            if war is None:
                continue
            if war['opponent']['name'] == clan.name:
                x = war['clan']
                war['clan'] = war['opponent']
                war['opponent'] = x
        war_prep = clash.convert_time( war['preparationStartTime'])
        war_start = clash.convert_time( war['startTime'])
        war_end = clash.convert_time( war['endTime'])

        if cd.time > war_prep and cd.time < war_start:
            cd.war_state = PREP
            message += '{} is in prep against {}\n'.format(clan.name, war['opponent']['name'])
        elif cd.time > war_start and cd.time < war_end:
            cd.war_state = BATTLE
            message += '{} is battling {}\n'.format(clan.name, war['opponent']['name'])
        elif cd.time > war_end:
            cd.war_state = ENDED
        else:
            raise ValueError('How did the logic die here?')
        cd.war_opponent = war['opponent']['tag'][1:]
        session.commit()
        
        print('Searching for members in {}'.format(war['clan']['name']))
        for mem in war['clan']['members']:
            member = session.query(Player).filter(Player.tag == mem['tag'][1:]).one()
            md = member.data[-1]
            ## B/c I messed up the table definition
            mdt = dt.datetime.strptime(md.time, '%Y-%m-%d %H:%M:%S.%f')
            if mdt > war_prep and mdt < war_start:
                md.war_state = PREP
            elif mdt > war_start and mdt < war_end:
                md.war_state = BATTLE
            elif mdt > war_end:
                md.war_state = ENDED
            md.in_war = True
            md.war_opponent = war['opponent']['tag'][1:]
            session.commit()
    session.close()
    return message    

