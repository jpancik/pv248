import sys
import sqlite3
from scorelib import load

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
        sql_script = sql_schema_file.read()

        db_cursor.executescript(sql_script)
        db_connection.commit()

    prints = load(input_filename)
    for print in prints:
        persist_print(db_cursor, print)

    db_connection.commit()
    db_connection.close()


main()