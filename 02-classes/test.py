import sys
from scorelib import load


def main():
    if len(sys.argv) >= 2:
        filename = sys.argv[1]
    else:
        print('You have to specify a filename as first argument.')
        return

    prints = load(filename)
    for item in prints:
        item.format()
        print('')

main()