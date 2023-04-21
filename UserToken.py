import configparser
import json

class UserToken:
    def __init__(self, config_file='config/config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        tokens = self.config.get("api_key", 'api_keys') or ''
        if tokens == '' :
            self.tokens = []
        else :
            self.tokens = json.loads(tokens) or []

    def is_valid(self, token):
        return (token in self.tokens)