#!/usr/bin/python
import sqlite3

def migrate():
	con = sqlite3.connect('proddata.db')
	con.row_factory = sqlite3.Row
	cur = con.cursor()
	cur.execute("CREATE TABLE MetronomeSetups("
				"id INTEGER PRIMARY KEY AUTOINCREMENT, phrase_id INTEGER, speed INTEGER, meter INTEGER, duration INTEGER, increment INTEGER, "\
				"FOREIGN KEY(phrase_id) REFERENCES Phrases(id))")
	con.commit()

if __name__ == "__main__":
	migrate()
