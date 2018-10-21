import json
import sqlite3
import sys


def main():
    if len(sys.argv) >= 2:
        composer_name_like = sys.argv[1]
    else:
        print('You have to specify a composer name as a first argument.')
        return

    db_connection = sqlite3.connect('scorelib.dat')
    db_cursor = db_connection.cursor()

    out = dict()
    for composer_name, print_id in db_cursor.execute(
            "SELECT person.name, p.id FROM person"
            " JOIN score_author sa ON sa.composer = person.id"
            " JOIN edition e ON e.score = sa.score"
            " JOIN print p ON  p.edition = e.id"
            " WHERE person.name LIKE ?", ('%{like_name}%'.format(like_name=composer_name_like),)).fetchall():

        print_row = db_cursor.execute("SELECT * FROM print WHERE print.id = ?", (print_id,)).fetchone()
        print_object = dict()
        print_object['Print Number'] = print_row[0]
        print_object['Partiture'] = True if (print_row[1] == 'Y') else False

        edition_id = print_row[2]
        edition_row = db_cursor.execute("SELECT * FROM edition WHERE edition.id = ?", (edition_id,)).fetchone()
        score_id = edition_row[1]
        print_object['Edition'] = edition_row[2]

        editors = []
        for name, born, died in db_cursor.execute(
                "SELECT name, born, died FROM edition_author ea JOIN person p ON p.id = ea.editor WHERE ea.edition = ?",
                (edition_id,)).fetchall():
            to_append = dict()

            if name:
                to_append['name'] = name
            if born:
                to_append['born'] = born
            if died:
                to_append['died'] = died

            editors.append(to_append)
        if editors:
            print_object['Editor'] = editors

        score_row = db_cursor.execute("SELECT * FROM score WHERE score.id = ?", (score_id,)).fetchone()
        print_object['Title'] = score_row[1]
        print_object['Genre'] = score_row[2]
        print_object['Key'] = score_row[3]
        print_object['Incipit'] = score_row[4]
        print_object['Publication Year'] = score_row[5]

        composers = []
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
        if composers:
            print_object['Composer'] = composers

        for number, name, range in db_cursor.execute(
                "SELECT number, name, range FROM voice v WHERE v.score = ? ORDER BY number",
                (score_id,)).fetchall():
            to_append = dict()

            if name:
                to_append['name'] = name
            if range:
                to_append['range'] = range

            if to_append:
                print_object['Voice %s' % number] = to_append

        if composer_name in out:
            out[composer_name].append(print_object)
        else:
            out[composer_name] = [print_object]

    print(json.dumps(out, indent=4, ensure_ascii=False))
    db_connection.close()

if __name__ == '__main__':
    main()