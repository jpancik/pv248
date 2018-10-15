import sqlite3
from scorelib import *


def main():
    db_connection = sqlite3.connect("scorelib.dat")
    db_cursor = db_connection.cursor()

    prints = []
    for print_row in db_cursor.execute("SELECT * FROM print").fetchall():
        print_id = print_row[0]
        partiture = True if (print_row[1] == 'Y') else False
        edition_id = print_row[2]

        edition_row = db_cursor.execute("SELECT * FROM edition WHERE edition.id = ?", (edition_id,)).fetchone()
        score_id = edition_row[1]
        edition_name = edition_row[2]

        editors = []
        for editor_row in db_cursor.execute("SELECT name, born, died FROM edition_author ea JOIN person p ON p.id = ea.editor WHERE ea.edition = ?", (edition_id,)).fetchall():
            editors.append(Person(editor_row[0], editor_row[1], editor_row[2]))

        score_row =  db_cursor.execute("SELECT * FROM score WHERE score.id = ?", (score_id,)).fetchone()
        score_name = score_row[1]
        score_genre = score_row[2]
        score_key = score_row[3]
        score_incipit = score_row[4]
        score_year = score_row[5]

        composers = []
        for composer_row in db_cursor.execute("SELECT name, born, died FROM score_author sa JOIN person p ON p.id = sa.composer WHERE sa.score = ?", (score_id,)).fetchall():
            composers.append(Person(composer_row[0], composer_row[1], composer_row[2]))

        voices = []
        for voice_row in db_cursor.execute("SELECT number, name, range FROM voice v WHERE v.score = ? ORDER BY number", (score_id,)).fetchall():
            voices.append(Voice(voice_row[0], voice_row[1], voice_row[2]))

        p = Print(print_id)
        p.partiture = partiture
        p.edition.authors = editors
        p.edition.name = edition_name
        p.composition().name = score_name
        p.composition().incipit = score_incipit
        p.composition().key = score_key
        p.composition().genre = score_genre
        p.composition().year = score_year
        p.composition().authors = composers
        p.composition().voices = voices
        prints.append(p)

    for p in prints:
        p.format()
        print('')

main()