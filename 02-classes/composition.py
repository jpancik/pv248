class Composition:
    def __init__(self):
        self.name = None
        self.incipit = None
        self.key = None
        self.genre = None
        self.voices = []
        self.authors = []

    def format_beginning(self):
        if self.authors:
            print("Composer: %s"
                  % ("; ".join([author.get_formatted() for author in self.authors])))

        if self.name:
            print('Title: %s' % self.name)

        if self.genre:
            print('Genre: %s' % self.genre)

        if self.key:
            print('Key: %s' % self.key)

    def format_end(self):
        if self.incipit:
            pass

        for index, voice in zip(range(len(self.voices)), self.voices):
            voice.format(index + 1)
