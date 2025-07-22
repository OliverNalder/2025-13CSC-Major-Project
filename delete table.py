import sqlite3

conn = sqlite3.connect("csv.db")
conn.execute("DROP TABLE team_1")
conn.execute("DELETE FROM _teams WHERE team_name='Wealthpoint_A'")
conn.execute("DELETE FROM _teams WHERE team_name='Wealthpoint_B'")
conn.execute("DELETE FROM _teams WHERE team_name='Wealthpoint_C'")
conn.commit()