import sqlite3 
import os 
from datetime import datetime

DB_PATH = '/workspaces/hr-policy-chatbot/hr-policy-chatbot/logs/query_log.db'

def init_db():
    os.makedirs(
        '/workspaces/hr-policy-chatbot/hr-policy-chatbot/logs',
        exist_ok=True
    )
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS query_log (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp     TEXT,
            employee_name TEXT,
            employee_id   TEXT,
            query         TEXT,
            answer        TEXT,
            confidence    INTEGER,
            escalated     INTEGER
        )
    ''')
    conn.commit()
    conn.close()
def log_query(employee_name, employee_id, query,
              answer, confidence, escalated):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        'INSERT INTO query_log VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)',
        (datetime.now().isoformat(), employee_name, employee_id,
         query, answer, confidence, int(escalated))
    )
    conn.commit()
    conn.close()