import json
import sqlite3
import sys


def main():
    if len(sys.argv) >= 2:
        print_id = sys.argv[1]
    else:
        print('You have to specify a print id as a first argument.')
        return

    db_connection = sqlite3.connect('scorelib.dat')
    db_cursor = db_connection.cursor()

    composers = []
    print_row = db_cursor.execute("SELECT * FROM print WHERE print.id = ?", (print_id,)).fetchone()
    edition_id = print_row[2]

    edition_row = db_cursor.execute("SELECT * FROM edition WHERE edition.id = ?", (edition_id,)).fetchone()
    score_id = edition_row[1]

    for name, born, died in db_cursor.execute(
            "SELECT name, born, died FROM score_author sa JOIN person p ON p.id = sa.composer WHERE sa.score = ?",
            (score_id,)).fetchall():
        to_append = dict()

        if name:
            to_append['name'] = name
        if born:
            to_append['born'] = born
        if died:
            to_append['died'] = died

        composers.append(to_append)

    print(json.dumps(composers, indent=4, ensure_ascii=False))
    db_connection.close()


if __name__ == '__main__':
    main()
