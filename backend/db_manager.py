import sqlite3

DB_NAME = "chess.db"

def get_connection():
    return sqlite3.connect(DB_NAME)


# ---------- GAME FUNCTIONS ----------

def create_game():
    conn = get_connection()
    cur = conn.cursor()

    initial_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    cur.execute("""
        INSERT INTO games (status, fen)
        VALUES (?, ?)
    """, ("ongoing", initial_fen))

    game_id = cur.lastrowid
    conn.commit()
    conn.close()
    return game_id


# ---------- MOVE FUNCTIONS ----------

def save_move(game_id, move_no, player, from_sq, to_sq):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO moves (game_id, move_no, player, from_sq, to_sq)
        VALUES (?, ?, ?, ?, ?)
    """, (game_id, move_no, player, from_sq, to_sq))

    conn.commit()
    conn.close()

