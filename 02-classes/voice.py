class Voice:
    def __init__(self, name, range):
        self.name = name
        self.range = range

    def format(self, index):
        if self.range:
            print('Voice %d: %s, %s' % (index, self.range, self.name))
        else:
            print('Voice %d: %s' % (index, self.name))
