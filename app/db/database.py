import sqlite3
import json
from datetime import datetime


class Database:

    def __init__(self, db_path="app.db"):
        self.db_path = db_path
        self.create_tables()

    def create_tables(self):

        conn = sqlite3.connect(self.db_path)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id TEXT,
            decision TEXT,
            confidence REAL,
            reason TEXT,
            latency REAL,
            created_at TEXT
        )
        """)

        conn.commit()
        conn.close()

    def insert_decision(self, state, latency):

        conn = sqlite3.connect(self.db_path)

        conn.execute("""
        INSERT INTO decisions (
            application_id,
            decision,
            confidence,
            reason,
            latency,
            created_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            state.application_id,
            state.decision,
            getattr(state, "confidence", None),
            json.dumps(state.reason),
            latency,
            datetime.utcnow().isoformat()
        ))

        conn.commit()
        conn.close()