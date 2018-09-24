import sys
import re


def get_composers(block):
    out = []
    name_regex = re.compile(r'([^;]*)')
    years_regex = re.compile(r'\([\d\-/]+\)')
    for line in block:
        if line.startswith('Composer:'):
            splitted = line.split(":")
            if len(splitted) == 2:
                names = splitted[1].strip()
                if names:
                    for name in name_regex.findall(names):
                        if name:
                            name = name.strip()
                            out.append(years_regex.sub('', name).strip())
    return out


def get_composition_century(block):
    regex_already_century = re.compile(r'^\d\dth century$')
    regex_year = re.compile(r'\d\d\d\d')
    for line in block:
        if line.startswith('Composition Year:'):
            splitted = line.split(":")
            if len(splitted) == 2:
                date = splitted[1].strip()
                if date:
                    if regex_already_century.fullmatch(date):
                        return date
                    else:
                        match = regex_year.findall(date)
                        if len(match) > 0:
                            # If year range, take the last year for composition century.
                            year = int(match[len(match)-1])
                            for i in range(10, 21):
                                if i * 100 < year <= (i + 1) * 100:
                                    return ('%sth century' % (i + 1)) if (i !=  20) else ('%sst century' % (i + 1))
    return None


def main():
    if len(sys.argv) >= 2:
        filename = sys.argv[1]
    else:
        print('You have to specify a filename as first argument.')
        return

    if len(sys.argv) >= 3:
        action = sys.argv[2]
    else:
        print('You have to specify an action as second argument.')
        return

    # Read input into blocks to parse. (Block is separated by empty lines.)
    current_block = []
    blocks = []
    for line in open(filename, 'r'):
        if line == '\n':
            blocks.append(current_block)
            current_block = []
        else:
            current_block.append(line)

    if action != 'composer' and action != 'century':
        print('Action %s is not defined.' % action)
        return

    stats = dict()
    for block in blocks:
        if action == 'composer':
            composers = get_composers(block)
            for composer in composers:
                if composer in stats:
                    stats[composer] += 1
                else:
                    stats[composer] = 1
        elif action == 'century':
            century = get_composition_century(block)
            if century:
                if century in stats:
                    stats[century] += 1
                else:
                    stats[century] = 1

    for key in stats.keys():
        print('%s: %s' % (key, stats[key]))


main()
