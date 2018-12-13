#!/usr/bin/env python3

import sys
import numpy as np
import pirata_codex as pc


if __name__ == '__main__':
    tracker = pc.activity.Activity_Tracker()
    tracker.create_activity_array()

    clan_list = np.sort(tracker.activity_array, order=['town_hall', 'total_heroes'])
    if len(sys.argv) < 2:
        print('No File name given, using default name')
        fname = 'clan_list.csv'
    else:
        fname = sys.argv[1]

    f = open(fname, 'w')
    f.write('Name, TH, BK, AQ, GW, Tot\n')
    x = lambda s: s.decode('utf-8', "ignore")

    for i in range(len(clan_list))[::-1]:
        f.write('{}, {}, {}, {}, {}, {}\n'.format(x(clan_list['names'][i]),
                                                  clan_list['town_hall'][i],
                                                  clan_list['barbarian_king'][i],
                                                  clan_list['archer_queen'][i],
                                                  clan_list['grand_warden'][i],
                                                  clan_list['total_heroes'][i]))
    f.close()

