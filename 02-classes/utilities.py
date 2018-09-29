import re
from scorelib import Print, Person, Voice

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

        if header == 'Composition Year':
            if re.match(r'^\d+$', content):
                out.composition().year = content

        if header == 'Edition':
            out.edition.name = content

        if header == 'Editor':
            if '(' in content:
                out.edition.authors.append(Person(content, None, None))
            else:
                names_regex = re.compile(r'(?:((?:\w)+(?:,)?(?: *)?(?:\w)*)(?:, *)?)')
                names = names_regex.findall(content)
                for name in names:
                    out.edition.authors.append(Person(name, None, None))

        if header.startswith('Voice'):
            range = None
            name = content

            match = re.match(r'^([^-]+--[^,\n]+)(?:(?:(,|;) )(.*))?', content)
            if match:
                range = match.group(1)
                name = match.group(2)

            out.composition().voices.append(Voice(name, range))

        if header == 'Partiture':
            if content == 'yes':
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
    name_regex = re.compile(r'^([^(]+)(?:\((\d*)(/\d)?--?(\d*)(/\d)?\))?$')
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
                    born = match.group(2)
                if not match.group(5):
                    died = match.group(4)
                out.append(Person(name, born, died))
    return out
