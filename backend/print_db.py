import sqlite3

DB_NAME = "chess.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

print("\n🎯 GAMES TABLE")
cursor.execute("SELECT * FROM games")
games = cursor.fetchall()
for row in games:
    print(row)

print("\n♟️ MOVES TABLE")
cursor.execute("SELECT * FROM moves")
moves = cursor.fetchall()
for row in moves:
    print(row)

conn.close()
