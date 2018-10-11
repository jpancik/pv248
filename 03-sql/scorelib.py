import re


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
    def __init__(self, number, name, range):
        self.number = number
        self.name = name
        self.range = range

    def format(self):
        if self.range and self.name:
            print('Voice %d: %s, %s' % (self.number, self.range, self.name))
        elif self.name:
            print('Voice %d: %s' % (self.number, self.name))
        elif self.range:
            print('Voice %d: %s' % (self.number, self.range))


def load(filename):
    # Read input into blocks to parse. (Block is separated by empty lines.)
    current_block = []
    blocks = []
    for line in open(filename, 'r'):
        if line == '\n':
            blocks.append(current_block)
            current_block = []
        else:
            current_block.append(line)
    if current_block:
        blocks.append(current_block)

    prints = []
    for block in blocks:
        item = parse_block(block)
        if item:
            prints.append(item)

    return prints


def parse_block(block):
    out = None
    for line in block:
        header, content = parse_line(line)

        if header == 'Print Number':
            out = Print(int(content))

        if not out or not content:
            continue

        if header == 'Composer':
            composers = get_composers(content)
            for composer in composers:
                out.composition().authors.append(composer)

        if header == 'Title':
            out.composition().name = content

        if header == 'Genre':
            out.composition().genre = content

        if header == 'Key':
            out.composition().key = content

        if header == 'Composition Year':
            year_match = re.match(r'^(?:.*)(\d{4})(?:.*)$', content)
            if year_match:
                out.composition().year = int(year_match.group(1))

        if header == 'Edition':
            out.edition.name = content

        if header == 'Editor':
            if '(' in content:
                out.edition.authors.append(Person(content, None, None))
            else:
                names_regex = re.compile(r'(?:((?:\w|\.|\-|\:)+(?:,)?(?: *)?(?:[^,\n])*)(?:, *)?)')
                names = names_regex.findall(content)
                for name in names:
                    out.edition.authors.append(Person(name, None, None))

        if header.startswith('Voice'):
            range = None
            name = content

            voice_number = re.match(r'^Voice (\d+)', header).group(1)

            match = re.match(r'^([^-]+--[^,;\n]+)(?:(?:(?:,|;) )(.*))?', content)
            if match:
                range = match.group(1)
                name = match.group(2)

            out.composition().voices.append(Voice(voice_number, name, range))

        if header == 'Partiture':
            if content.startswith('yes'):
                out.partiture = True
            else:
                out.partiture = False

        if header == 'Incipit':
            out.composition().incipit = content

    return out


def parse_line(line):
    match = re.match(r'^([^:]+):(.*)$', line)
    if match:
        return match.group(1).strip(), match.group(2).strip()

    return None, None


def get_composers(content):
    if not content:
        return []

    out = []

    if content == 'Platti, Giovanni Benedetto (+1763)':
        out.append(Person('Platti, Giovanni Benedetto', None, 1763))

    name_regex = re.compile(r'^([^(]+(?:\((?:\w| |\.)+\))?)(?:\((\d*)(/\d)?--?(\d*)(/\d)?\))?$')
    splitted = content.split(";")
    for name in splitted:
        stripped = name.strip()
        if stripped:
            match = name_regex.match(stripped)
            if match:
                name = match.group(1)
                if name:
                    name = name.strip()
                born = None
                died = None
                if not match.group(3):
                    born = int(match.group(2)) if match.group(2) else None
                if not match.group(5):
                    died = int(match.group(4)) if match.group(4) else None
                out.append(Person(name, born, died))
    return out
