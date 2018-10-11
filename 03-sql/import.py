import sqlite3
import sys

from pathlib import Path
from scorelib import load


def persist_people(db_cursor, print):
    for editor in print.edition.authors:
        persist_person(db_cursor, editor)

    for composer in print.composition().authors:
        persist_person(db_cursor, composer)


def persist_person(db_cursor, person):
    if int(db_cursor.execute("SELECT COUNT(*) FROM person p WHERE p.name = ?", (person.name,)).fetchone()[0]) == 0:
        db_cursor.execute(
            "INSERT INTO person ('born', 'died', 'name') VALUES (?, ?, ?)",
            (person.born, person.died, person.name))
    else:
        if person.born:
            db_cursor.execute("UPDATE person SET born=? WHERE name=?", (person.born, person.name))
        if person.died:
            db_cursor.execute("UPDATE person SET died=? WHERE name=?", (person.died, person.name))


def persist_print(db_cursor, print):
    pass


def main():
    if len(sys.argv) >= 2:
        input_filename = sys.argv[1]
    else:
        print('You have to specify an input filename as a first argument.')
        return

    if len(sys.argv) >= 3:
        output_filename = sys.argv[2]
    else:
        print('You have to specify an output filename as a second argument.')
        return

    db_connection = sqlite3.connect(output_filename)
    db_cursor = db_connection.cursor()

    sql_filename = 'scorelib.sql'
    with open(sql_filename, 'r') as sql_schema_file:
        db_file = Path("scorelib.dat")
        if not db_file.is_file():
            sql_script = sql_schema_file.read()

            db_cursor.executescript(sql_script)
            db_connection.commit()

    prints = load(input_filename)
    for print in prints:
        persist_people(db_cursor, print)

    for print in prints:
        persist_print(db_cursor, print)

    db_connection.commit()
    db_connection.close()


main()
