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
