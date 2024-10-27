import sqlite3
import json
import os

DBPATH = './bilinovel-config.db'

CREATE_CONFIG_TABLE_SQL = '''
CREATE TABLE IF NOT EXISTS config (
    config_dict VARCHAR(6) PRIMARY KEY,
    value TEXT
);
'''

initial_config = {"download_path": './', "theme": "Auto", "interval": "0", "numthread": '4'}

def initialize_db():
    if not os.path.exists(DBPATH):
        with sqlite3.connect(DBPATH) as conn:
            cursor = conn.cursor()
            cursor.execute(CREATE_CONFIG_TABLE_SQL)
            cursor.execute("INSERT OR REPLACE INTO config (config_dict, value) VALUES (?,?)", ("config", json.dumps(initial_config)))
            conn.commit()

def read_config_dict():
    with sqlite3.connect(DBPATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM config WHERE config_dict = \'config\';")
        result = cursor.fetchone()
        if result:
            return json.loads(result[0])
        return {}

def write_config_dict(key, value):
    """将配置字典写入数据库"""
    initialize_db()
    dict_data = read_config_dict()
    dict_data[key] = value
    with sqlite3.connect(DBPATH) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE config SET value = ? WHERE config_dict = ?", (json.dumps(dict_data), "config"))
        conn.commit()