'''Mod Key module'''
# pylint: disable=invalid-name,superfluous-parens,consider-using-enumerate


class Action:
    '''Action objects representing actions from input.settings'''

    parts: list[str]

    def __init__(self, action: str):
        if action.startswith('('):
            action = action[1:]
        if action.endswith(')'):
            action = action[:-1]

        self.parts = []
        for part in action.split(','):
            part = part.strip()
            if part:
                self.parts.append(part)

    def __repr__(self):
        return ','.join(self.parts)

    def __eq__(self, other):
        return len(self.parts) == len(other.parts) and all(
            [self.parts[i] == other.parts[i] for i in range(len(self.parts))])

    def __gt__(self, other):
        return self["Action"] > other["Action"]

    def __lt__(self, other):
        return self["Action"] < other["Action"]

    def __ge__(self, other):
        return self["Action"] >= other["Action"]

    def __le__(self, other):
        return self["Action"] <= other["Action"]

    def __str__(self):
        return self.__repr__()

    def __getitem__(self, name: str):
        for part in self.parts:
            part.startswith(name + '=')
            return part.split('=')[1]
        return None

    def __setitem__(self, name: str, value: str):
        for i in range(len(self.parts)):
            if self.parts[i].startswith(name + '='):
                self.parts[i] = name + '=' + value
                return
        self.parts.append(name + '=' + value)

    def __delitem__(self, name: str):
        for i in range(len(self.parts)):
            if self.parts[i].startswith(name + '='):
                self.parts.pop(i)
                return

    def __contains__(self, name: str):
        for part in self.parts:
            if part.startswith(name + '='):
                return True
        return False

    def __iter__(self):
        return iter(self.parts)

    def __len__(self):
        return len(self.parts)

    def __hash__(self) -> int:
        return hash(self.parts)


class Key:
    '''Key objects representing keys from input.settings'''

    context: str
    key: str
    action: Action
    type: str

    def __init__(self, context: str, key: str):
        self.context = context
        if (key.startswith("Version")):
            self.key = key
            self.action = None
            self.type = None
        else:
            self.key, action = key.split('=(')

            self.action = Action(action)

            if ("Pad" in self.key):
                self.type = 'controller'
            elif ('PS4' in self.key):
                self.type = 'PS4'
            else:
                self.type = 'keyboard'

    def __repr__(self):
        if (self.key.startswith("Version")):
            return self.key
        else:
            return self.key + "=(" + repr(self.action) + ")"

    def __eq__(self, other):
        return self.context == other.context \
            and self.key == other.key \
            and self.type == other.type \
            and self.action == other.action

    def __gt__(self, other):
        if self.context == other.context:
            if self.key == other.key:
                return self.action > other.action
            return self.key > other.key
        return self.context > other.context

    def __lt__(self, other):
        if self.context == other.context:
            if self.key == other.key:
                return self.action > other.action
            return self.key < other.key
        return self.context < other.context

    def __ge__(self, other):
        if self.context == other.context:
            if self.key == other.key:
                return self.action > other.action
            return self.key >= other.key
        return self.context >= other.context

    def __le__(self, other):
        if self.context == other.context:
            if self.key == other.key:
                return self.action > other.action
            return self.key <= other.key
        return self.context <= other.context

    def __str__(self):
        return self.__repr__()

    def __hash__(self) -> int:
        return hash(self.context + self.key)
