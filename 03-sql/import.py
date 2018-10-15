import sqlite3
import sys

from pathlib import Path
from scorelib import load


def persist_people(db_cursor, persisted_people, print):
    for editor in print.edition.authors:
        persist_person(db_cursor, persisted_people, editor)

    for composer in print.composition().authors:
        persist_person(db_cursor, persisted_people, composer)


def persist_person(db_cursor, persisted_people, person):
    if person.name not in persisted_people:
        db_cursor.execute(
            "INSERT INTO person ('born', 'died', 'name') VALUES (?, ?, ?)",
            (person.born, person.died, person.name))

        persisted_people[person.name] = db_cursor.lastrowid
    else:
        if person.born:
            db_cursor.execute("UPDATE person SET born=? WHERE name=?", (person.born, person.name))
        if person.died:
            db_cursor.execute("UPDATE person SET died=? WHERE name=?", (person.died, person.name))


def persist_score(db_cursor, persisted_people, persisted_scores, print):
    composition = print.composition()

    if composition not in persisted_scores:
        name = composition.name
        genre = composition.genre
        key = composition.key
        incipit = composition.incipit
        year = composition.year

        db_cursor.execute(
            "INSERT INTO score ('name', 'genre', 'key', 'incipit', 'year') VALUES (?, ?, ?, ?, ?)",
            (name, genre, key, incipit, year))
        score_id = db_cursor.lastrowid
        persisted_scores[composition] = score_id

        for voice in composition.voices:
            db_cursor.execute(
                "INSERT INTO voice ('number', 'score', 'range', 'name') VALUES (?, ?, ?, ?)",
                (voice.number, score_id, voice.range, voice.name))

        for author in composition.authors:
            author_id = persisted_people[author.name]
            db_cursor.execute(
                "INSERT INTO score_author ('score', 'composer') VALUES (?, ?)",
                (score_id, author_id))


def find_score_id(db_cursor, composition):
    return db_cursor.execute(
        "SELECT id FROM score s WHERE (s.name = ? AND s.genre = ? AND s.key = ? AND s.incipit = ? AND s.year = ?)",
        (composition.name, composition.genre, composition.key, composition.incipit, composition.year)).fetchone()[0]


def persist_edition(db_cursor, persisted_people, persisted_scores, persisted_editions, print):
    edition = print.edition

    if edition not in persisted_editions:
        score_id = persisted_scores[edition.composition]
        db_cursor.execute(
            "INSERT INTO edition ('score', 'name') VALUES (?, ?)",
            (score_id, edition.name))

        edition_id = db_cursor.lastrowid
        persisted_editions[edition] = edition_id

        for author in edition.authors:
            author_id = persisted_people[author.name]
            db_cursor.execute(
                "INSERT INTO edition_author ('edition', 'editor') VALUES (?, ?)",
                (edition_id, author_id))


def persist_print(db_cursor, persisted_editions, print):
    edition_id = persisted_editions[print.edition]
    db_cursor.execute(
        "INSERT INTO print ('id', 'partiture', 'edition') VALUES (?, ?, ?)",
        (print.print_id, ('Y' if print.partiture else 'N'), edition_id))


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

    db_file = Path("scorelib.dat")
    db_exists = db_file.is_file()

    db_connection = sqlite3.connect(output_filename)
    db_cursor = db_connection.cursor()

    sql_filename = 'scorelib.sql'
    with open(sql_filename, 'r') as sql_schema_file:
        if not db_exists:
            sql_script = sql_schema_file.read()

            db_cursor.executescript(sql_script)
            db_connection.commit()

    persisted_people = dict()
    persisted_scores = dict()
    persisted_editions = dict()

    prints = load(input_filename)
    for p in prints:
        persist_people(db_cursor, persisted_people, p)
        persist_score(db_cursor, persisted_people, persisted_scores, p)
        persist_edition(db_cursor, persisted_people, persisted_scores, persisted_editions, p)
        persist_print(db_cursor, persisted_editions, p)

    db_connection.commit()
    db_connection.close()


main()
