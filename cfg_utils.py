import sqlite3
import os

DBPATH = './bilinovel-config.db'

CREATE_CONFIG_TABLE_SQL = '''
CREATE TABLE IF NOT EXISTS config (
    KEY TEXT PRIMARY KEY,
    VALUE TEXT
);
'''

initial_config = {"download_path": './', "theme": "Auto", "interval": "0", "numthread": '4'}

def initialize_db():
    if not os.path.exists(DBPATH):
        with sqlite3.connect(DBPATH) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                KEY TEXT PRIMARY KEY,
                VALUE TEXT
            );
            ''')
            initial_config = {"download_path": './', "theme": "Auto", "interval": "0", "numthread": '4'}
            for key, value in initial_config.items():
                cursor.execute("INSERT OR REPLACE INTO config (KEY, VALUE) VALUES (?, ?)", (key, value))
            conn.commit()

def read_config_dict(key=None):
    with sqlite3.connect(DBPATH) as conn:
        cursor = conn.cursor()
        if key is None:
            return None
        else:
            cursor.execute("SELECT VALUE FROM config WHERE KEY = ?", (key,))
            result = cursor.fetchone()
            return result[0] if result else None

def write_config_dict(key, value):
    with sqlite3.connect(DBPATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO config (KEY, VALUE) VALUES (?, ?)", (key, value))
        conn.commit()