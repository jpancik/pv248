from composition import Composition

class Edition:
    def __init__(self):
        self.composition = Composition()
        self.authors = []
        self.name = None

    def format(self):
        self.composition.format_beginning()
        if self.name:
            print('Edition: %s' % self.name)
        self.composition.format_end()
        for author in self.authors:
            author.format()
