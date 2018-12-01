import requests
import json


class Discord:
    """ class for posting to discord"""

    def __init__(self, fname=None):
        if fname is None:
            fname = '../data/discord_info.json'
        with open(fname) as f:
            data = json.load(f)

        self.url = data['url']

    def send(self, message):
        requests.post(self.url, {'content':message} )
