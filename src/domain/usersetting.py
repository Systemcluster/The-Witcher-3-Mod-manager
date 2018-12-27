'''Usersetting module'''
# pylint: disable=invalid-name,superfluous-parens

class Usersetting:
    '''Usersetting objects representing user setting from user.settings'''

    def __init__(self, context: str, config: str):
        self.context = context
        self.option, self.value = config.split('=')

    def __repr__(self):
        return self.option + "=" + self.value
