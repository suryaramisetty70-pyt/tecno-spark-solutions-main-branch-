import sqlite3
import os
import json
from datetime import datetime

class OmniDatabase:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), '..', 'omni_society.db')
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Memory storage for agents to remember context
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT,
            directive TEXT,
            response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Tracking global tasks
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS global_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ceo_directive TEXT,
            status TEXT,
            final_report TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()

    def save_memory(self, agent_id: str, directive: str, response: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO memories (agent_id, directive, response) VALUES (?, ?, ?)',
                       (agent_id, directive, response))
        conn.commit()
        conn.close()

    def get_agent_memory(self, agent_id: str, limit=5):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT directive, response, timestamp FROM memories WHERE agent_id = ? ORDER BY timestamp DESC LIMIT ?', (agent_id, limit))
        rows = cursor.fetchall()
        conn.close()
        return [{"directive": r[0], "response": r[1], "time": r[2]} for r in rows]

OMNI_DB = OmniDatabase()
