'''Mod Key module'''
# pylint: disable=invalid-name,superfluous-parens

class Key:
    '''Key objects representing keys from input.settings'''

    def __init__(self, context, key):
        self.context = context

        self.key, action = key.split('=(')

        if ("Pad" in self.key):
            self.type = 'controller'
        elif ('PS4' in self.key):
            self.type = 'PS4'
        else:
            self.type = 'keyboard'

        action = action[:-1]
        values = action.split(',')
        self.action = values[0][7:]
        if self.action[-1] == ")":
            self.action = self.action[:-1]

        self.duration = ''
        self.axis = ''
        if (len(values) > 1):
            if ("Axis" in values[1]):
                self.axis = values[2][6:]
            elif ("Duration" in values[1]):
                self.duration = values[2][9:]

    def __repr__(self):
        string = ""
        string += self.key + "=(Action=" + self.action
        if (self.duration or self.axis):
            if (self.duration):
                string += ",State=Duration,IdleTime=" + self.duration
            else:
                string += ",State=Axis,Value=" + self.axis
        if string[-1] != ")":
            string += ")"
        return string
