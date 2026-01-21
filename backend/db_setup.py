import sqlite3

DB_NAME = "chess.db"

def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # ------------------ GAMES TABLE ------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fen TEXT NOT NULL,
        status TEXT DEFAULT 'ongoing',
        winner TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ------------------ MOVES TABLE ------------------
    cursor.execute("DROP TABLE IF EXISTS moves")

    cursor.execute("""
    CREATE TABLE moves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id INTEGER NOT NULL,
        from_sq TEXT NOT NULL,
        to_sq TEXT NOT NULL,
        move_no INTEGER NOT NULL,
        player TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (game_id) REFERENCES games(id)
    )
    """)

    conn.commit()
    conn.close()
    print("✅ chess.db created with games & moves tables (FINAL schema)")

if __name__ == "__main__":
    create_tables()
