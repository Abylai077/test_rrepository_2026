"""
Database handler for leaderboards using psycopg2.
Handles connection errors gracefully.
"""
import psycopg2
from datetime import datetime

# ========== CONFIGURATION ==========
# Use only ASCII characters to avoid UnicodeDecodeError.
DB_NAME = "snake_db"
DB_USER = "postgres"
DB_PASSWORD = "1234"
DB_HOST = "localhost"
# ===================================

_db_available = True

def get_connection():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST
        )
        return conn
    except Exception as e:
        global _db_available
        _db_available = False
        print(f"⚠️ Database connection failed: {e}")
        print("The game will continue without leaderboard features.")
        raise

def get_or_create_player(username):
    if not _db_available:
        return None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM players WHERE username = %s", (username,))
        row = cur.fetchone()
        if row:
            player_id = row[0]
        else:
            cur.execute("INSERT INTO players (username) VALUES (%s) RETURNING id", (username,))
            player_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return player_id
    except Exception:
        return None

def save_game_result(username, score, level):
    if not _db_available:
        return
    try:
        player_id = get_or_create_player(username)
        if player_id is None:
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO game_sessions (player_id, score, level_reached, played_at) VALUES (%s, %s, %s, %s)",
            (player_id, score, level, datetime.now())
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass

def get_top_10():
    if not _db_available:
        return []
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT players.username, game_sessions.score, game_sessions.level_reached,
                   game_sessions.played_at
            FROM game_sessions
            JOIN players ON players.id = game_sessions.player_id
            ORDER BY game_sessions.score DESC
            LIMIT 10
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception:
        return []

def get_personal_best(username):
    if not _db_available:
        return 0
    try:
        player_id = get_or_create_player(username)
        if player_id is None:
            return 0
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT MAX(score) FROM game_sessions WHERE player_id = %s", (player_id,))
        best = cur.fetchone()[0]
        cur.close()
        conn.close()
        return best if best is not None else 0
    except Exception:
        return 0