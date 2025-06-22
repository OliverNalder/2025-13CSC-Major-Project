import sqlite3
conn = sqlite3.connect('csv.db')
conn.execute("CREATE TABLE acc_info (acc_id INTEGER PRIMARY KEY, username char(100) NOT NULL, password char(100) NOT NULL, manager INTEGER)")
conn.execute("CREATE TABLE _teams (team_id INTEGER PRIMARY KEY, team_name char(100) NOT NULL)")
conn.execute("INSERT INTO _teams (team_name) VALUES ('Wealthpoint_A')")
conn.execute("CREATE TABLE team_1 (members)")
conn.commit()

