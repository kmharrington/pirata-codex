import requests
import json

from pirata_codex.config import *

class Discord:
    """ class for posting to discord"""

    def __init__(self, fname=None):
        if fname is None:
            fname = BASEDIR + 'data/discord_info.json'
        with open(fname) as f:
            data = json.load(f)

        self.url = data['url']

    def send(self, message):
        while message is not None:
            if len(message)>2000:
                piece = message[:2000]
                message = message[2000:]
            else:
                piece = message
                message = None
            requests.post(self.url, {'content': piece})

