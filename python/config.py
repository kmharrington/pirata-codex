import json

BASEDIR = '/home/pi/pirata-codex/'

#DB_NAME = BASEDIR + 'data/database.db'
INACTIVE = 0
ACTIVE = 1

with open(BASEDIR + 'data/configs.json') as f:
    configs = json.load(f)
