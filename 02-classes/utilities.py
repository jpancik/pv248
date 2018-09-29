import re
from print import Print
from person import Person

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

    prints = []
    for block in blocks:
        print = parse_block(block)
        if print:
            prints.append(print)

    return prints


def parse_block(block):
    out = None
    for line in block:
        header, content = parse_line(line)
        # print(header, content)

        if header == 'Print Number':
            out = Print(content)

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

        if header == 'Edition':
            out.edition.name = content

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
    name_regex = re.compile(r'^([^(]+)(?:\((\d*)--(\d*)\))?$')
    splitted = content.split(";")
    for name in splitted:
        stripped = name.strip()
        if stripped:
            match = name_regex.match(stripped)
            if match:
                name = match.group(1)
                if name:
                    name = name.strip()
                born = match.group(2)
                died = match.group(3)
                out.append(Person(name, born, died))
    return out
