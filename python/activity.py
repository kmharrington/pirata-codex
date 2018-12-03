import numpy as np
import datetime as dt

from sqlalchemy import desc

import pirata_codex as pc
from pirata_codex.database import (Clan, Clan_Data, Player, Player_Data)

def _player_data_time( player, time, equality, tol=dt.timedelta(days=1),
                        session=None):
    """
    return the Player_Data object before or after a specific time
    and within a specific tolerence

    args: 
        player - Player object
        time - time of interest
        equality - can be 'before' or 'after'
        tol - time tolerence
        session - database session
    returns:
        Player_Data object or None
    """
    assert (equality == 'before' or equality == 'after')
    if session is None:
        session = pc.get_session()

    pd = session.query(Player_Data).filter(Player_Data.player_tag == player.tag)
    if equality == 'before':
        pd = pd.filter(Player_Data.time <= time,
                       Player_Data.time >= time - tol)
        pd = pd.order_by( desc(Player_Data.time) ).first()
    else:
        pd = pd.filter(Player_Data.time >= time,
                       Player_Data.time <= time + tol)
        pd = pd.order_by( Player_Data.time ).first()
    return pd


def look_for_no_raids(time_limit=dt.timedelta(7), t1=dt.datetime.now(),
                        old_limit=dt.timedelta(1),
                        exclude_list = []):
    """
    Look for members with no raids in the last week and builds message
    with their names

    args:
        time_limit - dt.timedelta where there have been no raids
        t1 - reference time. Will this ever not be right now?
        old_limit - dt.timedelta of how old the data should be to compare
        exclude_list - list of clan tags where, if player is in that clan,
                       we do not add them to the message
    returns:
        message of players with no raids
    """

    session = pc.get_session()
    players = session.query(Player).filter(Player.status == pc.ACTIVE).all()
    
    message = 'Checked players resource grabs\n'

    for player in players:
        p0 = _player_data_time(player, t1 - time_limit, 'before', 
                    tol=dt.timedelta(14), session=session)
        if p0 is None:
            # if player has not been around long enough
            # print('{} has not been around for {} days'.format(player.name,
            #                                                  time_limit.days))
            continue
        p1 = _player_data_time(player, t1 - old_limit, 'after', session=session)
        if p1 is None:
            raise ValueError('no recent enough player data for {}'.format(player.name))
        
        if (p0.gold_total == p1.gold_total and p0.elixer_total == p1.elixer_total
                and p0.de_total == p1.de_total):
            if p1.current_clan_tag in exclude_list:
                continue
            message += '{} has not raided in at least {} days\n'.format(player.name,
                                                            (time_limit - old_limit).days)

    return message


if __name__ == "__main__":
    look_for_no_raids(time_limit=dt.timedelta(7),
                    exclude_list=['GYR0RRJ'])


