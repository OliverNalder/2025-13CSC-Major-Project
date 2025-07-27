import sqlite3

conn = sqlite3.connect("csv.db")
conn.execute("DROP TABLE asd")
conn.execute("DELETE FROM _teams WHERE team_name='asd'")
conn.commit()