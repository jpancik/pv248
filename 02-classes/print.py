from edition import Edition

class Print:
    def __init__(self, print_id):
        self.print_id = print_id
        self.edition = Edition()
        self.partiture = None

    def format(self):
        print('Print number: %s' % self.print_id)
        self.edition.format()

    def composition(self):
        if self.edition:
            return self.edition.composition