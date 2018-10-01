class Print:
    def __init__(self, print_id):
        self.print_id = print_id
        self.edition = Edition()
        self.partiture = None

    def format(self):
        print('Print Number: %s' % self.print_id)
        self.edition.format()

        if not self.partiture:
            self.partiture = False
        print('Partiture: %s' % ('yes' if self.partiture else 'no'))

        if self.composition().incipit:
            print('Incipit: %s' % self.composition().incipit)

    def composition(self):
        if self.edition:
            return self.edition.composition


class Edition:
    def __init__(self):
        self.composition = Composition()
        self.authors = []
        self.name = None

    def format(self):
        self.composition.format_beginning()
        if self.name:
            print('Edition: %s' % self.name)
        if self.authors:
            print("Editor: %s"
                  % (", ".join([author.get_formatted() for author in self.authors])))
        self.composition.format_end()

class Composition:
    def __init__(self):
        self.name = None
        self.incipit = None
        self.key = None
        self.genre = None
        self.year = None
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

        if self.year:
            print('Composition Year: %s' % self.year)

    def format_end(self):
        for index, voice in zip(range(len(self.voices)), self.voices):
            voice.format(index + 1)


class Person:
    def __init__(self, name, born, died):
        self.name = name
        self.born = born
        self.died = died

    def get_formatted(self):
        if self.born and self.died:
            return "%s (%s--%s)" % (self.name, self.born, self.died)
        elif self.born and not self.died:
            return "%s (%s--)" % (self.name, self.born)
        elif not self.born and self.died:
            return "%s (--%s)" % (self.name, self.died)
        else:
            return "%s" % self.name


class Voice:
    def __init__(self, name, range):
        self.name = name
        self.range = range

    def format(self, index):
        if self.range and self.name:
            print('Voice %d: %s, %s' % (index, self.range, self.name))
        elif self.name:
            print('Voice %d: %s' % (index, self.name))
        elif self.range:
            print('Voice %d: %s' % (index, self.range))
