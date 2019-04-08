import requests
import json

from pirata_codex.config import *

class Discord:
    """ class for posting to discord"""

    def __init__(self):
        self.configs = configs['discord']

    def _send(self, url, message):
        '''
        makes sure the message is short enough to 
        get posted onto discord
        '''
        while message is not None:
            if len(message)>2000:
                piece = message[:2000]
                message = message[2000:]
            else:
                piece = message
                message = None
            requests.post(url, {'content': piece})
    
    def send(self, message):
        self._send(self.configs['tracker_url'], message)
        
    def announce(self, message):
        self._send(self.configs['announce_url'], message)

